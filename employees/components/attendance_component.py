from datetime import timedelta, timezone

from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.employee_component import EmployeeComponent
from employees.components.shift_component import ShiftComponent
from employees.components.validation import load_schema
from employees.repositories.attendance_repository import AttendanceRepository
from employees.serializers.attendance_serializer import (
    ClockInInputSchema,
    ClockOutInputSchema,
)
from employees.serializers.shift_serializer import to_utc_naive
from employees.sqlalchemy_db import db_session


class AttendanceComponent:
    LATE_GRACE = timedelta(minutes=5)
    EARLY_THRESHOLD = timedelta(minutes=15)
    MAX_EARLY_CLOCK_IN = timedelta(hours=2)
    MAX_WORK_DURATION = timedelta(hours=24)

    def __init__(
        self,
        repository=None,
        shift_component=None,
        employee_component=None,
    ):
        self.repository = repository or AttendanceRepository()
        self.shift_component = shift_component or ShiftComponent()
        self.employee_component = employee_component or EmployeeComponent()

    def list_employee_attendance(self, employee_id):
        self.employee_component.get_employee(employee_id)
        return self.repository.list_employee_records(employee_id)

    def get_attendance(self, attendance_id):
        attendance = self.repository.get_by_id(attendance_id)
        if attendance is None:
            raise NotFound({"attendance": "Attendance record does not exist."})
        return attendance

    def clock_in(self, shift_id, data, actor_username=None):
        values = load_schema(ClockInInputSchema(), data)
        clock_in = values["clock_in"]
        note = values.get("note")
        if note is not None:
            note = note.strip() or None

        shift = self.shift_component.get_shift(shift_id)
        shift_start = self._aware(shift.start_datetime)
        shift_end = self._aware(shift.end_datetime)

        if clock_in < shift_start - self.MAX_EARLY_CLOCK_IN:
            raise ValidationError({
                "clock_in": "Clock in cannot be more than two hours before the shift."
            })
        if clock_in >= shift_end:
            raise ValidationError({
                "clock_in": "Clock in must happen before the scheduled shift ends."
            })

        if self.repository.get_by_shift(shift_id):
            raise ValidationError({"shift_id": "This shift already has attendance."})

        if clock_in > shift_start + self.LATE_GRACE:
            arrival_status = "LATE"
        elif clock_in < shift_start - self.EARLY_THRESHOLD:
            arrival_status = "EARLY"
        else:
            arrival_status = "ON_TIME"

        try:
            attendance = self.repository.create({
                "employee_id": shift.employee_id,
                "shift_id": shift.id,
                "clock_in": to_utc_naive(clock_in),
                "status": "CLOCKED_IN",
                "arrival_status": arrival_status,
                "note": note,
            })
            self.repository.add_audit_log(
                actor_username,
                "EMPLOYEE_CLOCKED_IN",
                attendance,
            )
            db_session.commit()
            return attendance
        except IntegrityError as exc:
            db_session.rollback()
            raise ValidationError({"shift_id": "This shift already has attendance."}) from exc
        except Exception:
            db_session.rollback()
            raise

    def clock_out(self, attendance_id, data, actor_username=None):
        values = load_schema(ClockOutInputSchema(), data)
        clock_out = values["clock_out"]

        try:
            attendance = self.repository.get_by_id(attendance_id, lock=True)
            if attendance is None:
                raise NotFound({"attendance": "Attendance record does not exist."})
            if attendance.status == "COMPLETED":
                raise ValidationError({"attendance": "Employee already clocked out."})

            clock_in = self._aware(attendance.clock_in)
            if clock_out <= clock_in:
                raise ValidationError({
                    "clock_out": "Clock out must be after clock in."
                })
            if clock_out - clock_in > self.MAX_WORK_DURATION:
                raise ValidationError({
                    "clock_out": "Attendance duration cannot exceed 24 hours."
                })

            worked_minutes = int((clock_out - clock_in).total_seconds() // 60)
            attendance.clock_out = to_utc_naive(clock_out)
            attendance.worked_minutes = worked_minutes
            attendance.status = "COMPLETED"

            if "note" in values:
                note = values.get("note")
                attendance.note = note.strip() if note and note.strip() else None

            self.repository.add_audit_log(
                actor_username,
                "EMPLOYEE_CLOCKED_OUT",
                attendance,
            )
            db_session.commit()
            return attendance
        except (NotFound, ValidationError):
            db_session.rollback()
            raise
        except Exception:
            db_session.rollback()
            raise

    @staticmethod
    def _aware(value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
