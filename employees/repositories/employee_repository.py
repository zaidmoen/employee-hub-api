from employees.models import Employee
from employees.sqlalchemy_db import db_session

class EmployeeRepository:
    def get_all(self):
        query = db_session.query(Employee).order_by(Employee.id)
        return query.all()

    def get_by_id(self, employee_id, lock=False):
        query = db_session.query(Employee).filter(Employee.id == employee_id)
        if lock:
            query = query.with_for_update()
        return query.first()

    def get_by_email(self, email):
        return db_session.query(Employee).filter(Employee.email == email).first()

    def create(self, values):
        employee = Employee(**values)
        db_session.add(employee)
        db_session.flush()
        return employee
