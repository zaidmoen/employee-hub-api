from employees.models import Department, EmployeeProfile, JobPosition
from employees.sqlalchemy_db import db_session


class OrganizationRepository:
    def list_departments(self):
        return db_session.query(Department).order_by(Department.name).all()

    def get_department(self, department_id):
        return (
            db_session.query(Department)
            .filter(Department.id == department_id)
            .first()
        )

    def get_department_by_code(self, code):
        return (
            db_session.query(Department)
            .filter(Department.code == code)
            .first()
        )

    def create_department(self, values):
        department = Department(**values)
        db_session.add(department)
        db_session.flush()
        return department

    def list_positions(self, department_id=None):
        query = db_session.query(JobPosition)
        if department_id is not None:
            query = query.filter(JobPosition.department_id == department_id)
        return query.order_by(JobPosition.title).all()

    def get_position(self, position_id):
        return (
            db_session.query(JobPosition)
            .filter(JobPosition.id == position_id)
            .first()
        )

    def get_position_by_code(self, code):
        return (
            db_session.query(JobPosition)
            .filter(JobPosition.code == code)
            .first()
        )

    def create_position(self, values):
        position = JobPosition(**values)
        db_session.add(position)
        db_session.flush()
        return position

    def get_profile(self, employee_id):
        return (
            db_session.query(EmployeeProfile)
            .filter(EmployeeProfile.employee_id == employee_id)
            .first()
        )

    def get_profile_by_number(self, employee_number):
        return (
            db_session.query(EmployeeProfile)
            .filter(EmployeeProfile.employee_number == employee_number)
            .first()
        )

    def create_profile(self, values):
        profile = EmployeeProfile(**values)
        db_session.add(profile)
        db_session.flush()
        return profile
