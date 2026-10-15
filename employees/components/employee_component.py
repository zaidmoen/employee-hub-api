from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.validation import load_schema
from employees.repositories.employee_repository import EmployeeRepository
from employees.repositories.rate_repository import RateRepository
from employees.serializers.employee_serializer import EmployeeInputSchema
from employees.serializers.rate_serializer import EmployeeRateChangeInputSchema
from employees.sqlalchemy_db import db_session


class EmployeeComponent:
    def __init__(self, repository=None, rate_repository=None):
        self.repository = repository or EmployeeRepository()
        self.rate_repository = rate_repository or RateRepository()

    def list_employees(self):
        return self.repository.get_all()

    def get_employee(self, employee_id, lock=False):
        employee = self.repository.get_by_id(employee_id, lock=lock)
        if employee is None:
            raise NotFound({"employee": "Employee does not exist."})
        return employee

    def create_employee(self, data):
        values = load_schema(EmployeeInputSchema(), data)
        values["first_name"] = values["first_name"].strip()
        values["last_name"] = values["last_name"].strip()
        values["email"] = values["email"].strip().lower()
        values["phone_number"] = values["phone_number"].strip()

        if not all((values["first_name"], values["last_name"], values["phone_number"])):
            raise ValidationError({"detail": "Employee text fields cannot be blank."})

        try:
            if self.repository.get_by_email(values["email"]):
                raise ValidationError({"email": "This email is already in use."})
            employee = self.repository.create(values)
            db_session.commit()
            return employee
        except IntegrityError as exc:
            db_session.rollback()
            raise ValidationError({"email": "This email is already in use."}) from exc
        except Exception:
            db_session.rollback()
            raise

    def update_hourly_rate(self, employee_id, data, actor_username=None):
        values = load_schema(EmployeeRateChangeInputSchema(), data)
        reason = values.get("reason")
        if reason is not None:
            reason = reason.strip() or None

        try:
            employee = self.get_employee(employee_id, lock=True)
            old_rate = employee.hourly_rate
            new_rate = values["hourly_rate"]

            if old_rate == new_rate:
                raise ValidationError({
                    "hourly_rate": "New hourly rate must be different from the current rate."
                })

            employee.hourly_rate = new_rate
            self.rate_repository.create_history({
                "employee_id": employee_id,
                "old_rate": old_rate,
                "new_rate": new_rate,
                "reason": reason,
                "changed_by": actor_username,
            })
            self.rate_repository.add_audit_log(
                actor_username,
                employee_id,
                old_rate,
                new_rate,
                reason,
            )
            db_session.commit()
            return employee
        except (NotFound, ValidationError):
            db_session.rollback()
            raise
        except Exception:
            db_session.rollback()
            raise

    def list_rate_history(self, employee_id):
        self.get_employee(employee_id)
        return self.rate_repository.list_history(employee_id)
