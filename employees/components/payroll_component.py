from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.validation import load_schema
from employees.repositories.attendance_repository import AttendanceRepository
from employees.repositories.employee_repository import EmployeeRepository
from employees.repositories.payroll_repository import PayrollRepository
from employees.repositories.shift_repository import ShiftRepository
from employees.serializers.payroll_serializer import PayrollPeriodInputSchema
from employees.sqlalchemy_db import db_session


class PayrollComponent:
    OVERTIME_MULTIPLIER = Decimal("1.50")

    def __init__(
        self,
        repository=None,
        employee_repository=None,
        attendance_repository=None,
        shift_repository=None,
    ):
        self.repository = repository or PayrollRepository()
        self.employee_repository = employee_repository or EmployeeRepository()
        self.attendance_repository = attendance_repository or AttendanceRepository()
        self.shift_repository = shift_repository or ShiftRepository()

    def list_periods(self):
        return self.repository.list_periods()

    def get_period(self, period_id):
        period = self.repository.get_period(period_id)
        if period is None:
            raise NotFound({"payroll_period": "Payroll period does not exist."})
        return period

    def create_period(self, data, actor_username=None):
        values = load_schema(PayrollPeriodInputSchema(), data)

        try:
            period = self.repository.create_period(values)
            self.repository.add_audit_log(
                actor_username,
                "PAYROLL_PERIOD_CREATED",
                period.id,
                details=f"{period.start_date} to {period.end_date}",
            )
            db_session.commit()
            return period
        except IntegrityError as exc:
            db_session.rollback()
            raise ValidationError({
                "detail": "A payroll period with this date range already exists."
            }) from exc
        except Exception:
            db_session.rollback()
            raise

    def list_records(self, period_id):
        self.get_period(period_id)
        return self.repository.list_records(period_id)

    def calculate_period(self, period_id, actor_username=None):
        try:
            period = self.repository.get_period(period_id, lock=True)
            if period is None:
                raise NotFound({"payroll_period": "Payroll period does not exist."})
            if period.status == "FINALIZED":
                raise ValidationError({
                    "payroll_period": "Finalized payroll cannot be recalculated."
                })

            start_datetime = datetime.combine(period.start_date, time.min)
            end_datetime = datetime.combine(
                period.end_date + timedelta(days=1),
                time.min,
            )

            self.repository.delete_records(period_id)
            employees = self.employee_repository.get_all()
            created_records = []

            for employee in employees:
                attendance_records = self.attendance_repository.get_completed_between(
                    employee.id,
                    start_datetime,
                    end_datetime,
                )
                if not attendance_records:
                    continue

                regular_minutes = 0
                overtime_minutes = 0
                gross_pay = Decimal("0.00")

                for attendance in attendance_records:
                    shift = self.shift_repository.get_by_id(attendance.shift_id)
                    if shift is None or attendance.worked_minutes is None:
                        continue

                    scheduled_minutes = int(
                        (shift.end_datetime - shift.start_datetime).total_seconds() // 60
                    )
                    worked_minutes = max(attendance.worked_minutes, 0)
                    regular = min(worked_minutes, scheduled_minutes)
                    overtime = max(worked_minutes - scheduled_minutes, 0)

                    regular_minutes += regular
                    overtime_minutes += overtime

                    rate = shift.hourly_rate_snapshot
                    regular_pay = (
                        Decimal(regular) / Decimal("60")
                    ) * rate
                    overtime_pay = (
                        Decimal(overtime) / Decimal("60")
                    ) * rate * self.OVERTIME_MULTIPLIER
                    gross_pay += regular_pay + overtime_pay

                gross_pay = gross_pay.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
                record = self.repository.create_record({
                    "payroll_period_id": period.id,
                    "employee_id": employee.id,
                    "regular_minutes": regular_minutes,
                    "overtime_minutes": overtime_minutes,
                    "gross_pay": gross_pay,
                })
                created_records.append(record)

            period.status = "CALCULATED"
            self.repository.add_audit_log(
                actor_username,
                "PAYROLL_CALCULATED",
                period.id,
                details=f"records={len(created_records)}",
            )
            db_session.commit()
            return period, created_records
        except (NotFound, ValidationError):
            db_session.rollback()
            raise
        except Exception:
            db_session.rollback()
            raise

    def finalize_period(self, period_id, actor_username=None):
        try:
            period = self.repository.get_period(period_id, lock=True)
            if period is None:
                raise NotFound({"payroll_period": "Payroll period does not exist."})
            if period.status != "CALCULATED":
                raise ValidationError({
                    "payroll_period": "Payroll must be calculated before finalizing."
                })

            period.status = "FINALIZED"
            self.repository.add_audit_log(
                actor_username,
                "PAYROLL_FINALIZED",
                period.id,
            )
            db_session.commit()
            return period
        except (NotFound, ValidationError):
            db_session.rollback()
            raise
        except Exception:
            db_session.rollback()
            raise
