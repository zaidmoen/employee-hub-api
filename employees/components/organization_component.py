from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.employee_component import EmployeeComponent
from employees.components.validation import load_schema
from employees.repositories.organization_repository import OrganizationRepository
from employees.serializers.organization_serializer import (
    DepartmentInputSchema,
    EmployeeProfileInputSchema,
    PositionInputSchema,
)
from employees.sqlalchemy_db import db_session


class OrganizationComponent:
    def __init__(self, repository=None, employee_component=None):
        self.repository = repository or OrganizationRepository()
        self.employee_component = employee_component or EmployeeComponent()

    def list_departments(self):
        return self.repository.list_departments()

    def create_department(self, data):
        values = load_schema(DepartmentInputSchema(), data)
        values["name"] = values["name"].strip()
        values["code"] = values["code"].strip().upper()

        if not values["name"] or not values["code"]:
            raise ValidationError({"detail": "Department name and code are required."})

        if self.repository.get_department_by_code(values["code"]):
            raise ValidationError({"code": "Department code already exists."})

        try:
            department = self.repository.create_department(values)
            db_session.commit()
            return department
        except IntegrityError as exc:
            db_session.rollback()
            raise ValidationError({"detail": "Department already exists."}) from exc
        except Exception:
            db_session.rollback()
            raise

    def list_positions(self, department_id=None):
        if department_id is not None and not self.repository.get_department(department_id):
            raise NotFound({"department": "Department does not exist."})
        return self.repository.list_positions(department_id)

    def create_position(self, data):
        values = load_schema(PositionInputSchema(), data)
        values["title"] = values["title"].strip()
        values["code"] = values["code"].strip().upper()

        if not self.repository.get_department(values["department_id"]):
            raise ValidationError({"department_id": "Department does not exist."})
        if self.repository.get_position_by_code(values["code"]):
            raise ValidationError({"code": "Position code already exists."})

        try:
            position = self.repository.create_position(values)
            db_session.commit()
            return position
        except IntegrityError as exc:
            db_session.rollback()
            raise ValidationError({"detail": "Position already exists."}) from exc
        except Exception:
            db_session.rollback()
            raise

    def get_employee_profile(self, employee_id):
        self.employee_component.get_employee(employee_id)
        profile = self.repository.get_profile(employee_id)
        if profile is None:
            raise NotFound({"profile": "Employee profile does not exist."})
        return profile

    def set_employee_profile(self, employee_id, data):
        self.employee_component.get_employee(employee_id)
        values = load_schema(EmployeeProfileInputSchema(), data)
        values["employee_number"] = values["employee_number"].strip().upper()

        manager_id = values.get("manager_id")
        if manager_id == employee_id:
            raise ValidationError({"manager_id": "Employee cannot manage themselves."})
        if manager_id is not None:
            self.employee_component.get_employee(manager_id)

        department_id = values.get("department_id")
        if department_id is not None and not self.repository.get_department(department_id):
            raise ValidationError({"department_id": "Department does not exist."})

        position_id = values.get("position_id")
        position = None
        if position_id is not None:
            position = self.repository.get_position(position_id)
            if position is None:
                raise ValidationError({"position_id": "Position does not exist."})
            if department_id is not None and position.department_id != department_id:
                raise ValidationError({
                    "position_id": "Position must belong to the selected department."
                })
            if department_id is None:
                values["department_id"] = position.department_id

        existing_number = self.repository.get_profile_by_number(values["employee_number"])
        if existing_number and existing_number.employee_id != employee_id:
            raise ValidationError({"employee_number": "Employee number already exists."})

        try:
            profile = self.repository.get_profile(employee_id)
            if profile is None:
                values["employee_id"] = employee_id
                profile = self.repository.create_profile(values)
            else:
                for key, value in values.items():
                    setattr(profile, key, value)
            db_session.commit()
            return profile
        except IntegrityError as exc:
            db_session.rollback()
            raise ValidationError({"detail": "Could not save employee profile."}) from exc
        except Exception:
            db_session.rollback()
            raise
