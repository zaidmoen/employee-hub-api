from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.validation import load_schema
from employees.repositories.employee_repository import EmployeeRepository
from employees.serializers.employee_serializer import EmployeeInputSchema, EmployeeRateInputSchema
from employees.sqlalchemy_db import db_session

class EmployeeComponent:
    def __init__(self, repository=None):
        self.repository = repository or EmployeeRepository()
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
    def update_hourly_rate(self, employee_id, data):
        values = load_schema(EmployeeRateInputSchema(), data)
        employee = self.get_employee(employee_id, lock=True)
        employee.hourly_rate = values["hourly_rate"]
        db_session.commit()
        return employee
