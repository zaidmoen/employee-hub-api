from datetime import datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from rest_framework.exceptions import APIException, NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.employee_component import EmployeeComponent
from employees.components.validation import load_schema
from employees.repositories.shift_repository import ShiftRepository
from employees.serializers.shift_serializer import (
    ForecastQuerySchema,
    ShiftInputSchema,
    ShiftListQuerySchema,
    ShiftUpdateInputSchema,
    to_utc_naive,
)
from employees.sqlalchemy_db import db_session


class ShiftConflict(APIException):
    status_code = 409
    default_detail = "The shift conflicts with an existing shift."
    default_code = "shift_conflict"


class ShiftComponent:
    MAX_DURATION = timedelta(hours=24)

    def __init__(self, repository=None, employee_component=None):
        self.repository = repository or ShiftRepository()
        self.employee_component = employee_component or EmployeeComponent()

    def list_shifts(self, employee_id, query_params):
        # Check the employee first so an unknown employee gets a 404 response.
        self.employee_component.get_employee(employee_id)
        values = load_schema(ShiftListQuerySchema(), query_params)

        start = self._date_start(values.get("from_date"))
        end_date = values.get("to_date")
        end = None
        if end_date:
            end = self._date_start(end_date + timedelta(days=1))

        return self.repository.get_employee_shifts(employee_id, start, end)

    def create_shift(self, employee_id, data):
        values = load_schema(ShiftInputSchema(), data)
        start = values["start_datetime"]
        end = values["end_datetime"]
        self._validate_duration(start, end)

        try:
            # Lock the employee row while checking and creating this shift.
            employee = self.employee_component.get_employee(employee_id, lock=True)
            self._raise_if_overlap(employee_id, start, end)

            shift = self.repository.create(
                employee_id,
                to_utc_naive(start),
                to_utc_naive(end),
                employee.hourly_rate,
            )
            db_session.commit()
            return shift
        except IntegrityError as exc:
            db_session.rollback()
            raise ShiftConflict() from exc
        except Exception:
            db_session.rollback()
            raise

    def get_shift(self, shift_id):
        shift = self.repository.get_by_id(shift_id)
        if shift is None:
            raise NotFound({"shift": "Shift does not exist."})
        return shift

    def update_shift(self, shift_id, data):
        try:
            shift = self.repository.get_by_id(shift_id)
            if shift is None:
                raise NotFound({"shift": "Shift does not exist."})

            self.employee_component.get_employee(shift.employee_id, lock=True)
            shift = self.repository.get_by_id(shift_id, lock=True)
            values = load_schema(ShiftUpdateInputSchema(), data)

            start = values.get("start_datetime", self._aware(shift.start_datetime))
            end = values.get("end_datetime", self._aware(shift.end_datetime))
            self._validate_duration(start, end)
            self._raise_if_overlap(
                shift.employee_id,
                start,
                end,
                exclude_id=shift_id,
            )

            shift.start_datetime = to_utc_naive(start)
            shift.end_datetime = to_utc_naive(end)
            db_session.commit()
            return shift
        except (NotFound, ValidationError):
            db_session.rollback()
            raise
        except IntegrityError as exc:
            db_session.rollback()
            raise ShiftConflict() from exc
        except Exception:
            db_session.rollback()
            raise

    def delete_shift(self, shift_id):
        shift = self.repository.get_by_id(shift_id)
        if shift is None:
            raise NotFound({"shift": "Shift does not exist."})

        db_session.delete(shift)
        db_session.commit()

    def forecast_summary(self, employee_id, query_params):
        self.employee_component.get_employee(employee_id)
        values = load_schema(ForecastQuerySchema(), query_params)

        start = self._date_start(values["from_date"])
        end = self._date_start(values["to_date"] + timedelta(days=1))
        shifts = self.repository.get_employee_shifts(employee_id, start, end)

        total_hours = sum((self._hours(shift) for shift in shifts), Decimal("0"))
        total_pay = sum((self._pay(shift) for shift in shifts), Decimal("0"))
        rounded_hours = total_hours.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        rounded_pay = total_pay.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        return {
            "employee_id": employee_id,
            "from": values["from_date"].isoformat(),
            "to": values["to_date"].isoformat(),
            "shift_count": len(shifts),
            "scheduled_hours": f"{rounded_hours:.2f}",
            "forecasted_pay": f"{rounded_pay:.2f}",
        }

    def _raise_if_overlap(self, employee_id, start, end, exclude_id=None):
        conflict = self.repository.find_overlap(
            employee_id,
            to_utc_naive(start),
            to_utc_naive(end),
            exclude_id,
        )
        if conflict:
            raise ShiftConflict({
                "detail": f"This time overlaps scheduled shift {conflict.id}."
            })

    @classmethod
    def _validate_duration(cls, start, end):
        if end <= start:
            raise ValidationError({"end_datetime": "End time must be after start time."})
        if end - start > cls.MAX_DURATION:
            raise ValidationError({"end_datetime": "A shift cannot exceed 24 hours."})

    @staticmethod
    def _date_start(value):
        if value is None:
            return None
        start = datetime.combine(value, time.min)
        return start.replace(tzinfo=timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _aware(value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @classmethod
    def _hours(cls, shift):
        start = cls._aware(shift.start_datetime)
        end = cls._aware(shift.end_datetime)
        duration_minutes = int((end - start).total_seconds() // 60)
        return Decimal(duration_minutes) / Decimal("60")

    @classmethod
    def _pay(cls, shift):
        return cls._hours(shift) * shift.hourly_rate_snapshot
