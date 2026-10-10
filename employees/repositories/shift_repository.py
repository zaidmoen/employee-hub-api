from employees.models import ScheduledShift
from employees.sqlalchemy_db import db_session

class ShiftRepository:
    def get_by_id(self, shift_id, lock=False):
        query = db_session.query(ScheduledShift).filter(ScheduledShift.id == shift_id)
        if lock:
            query = query.with_for_update()
        return query.first()

    def get_employee_shifts(self, employee_id, start=None, end=None):
        query = db_session.query(ScheduledShift).filter(
            ScheduledShift.employee_id == employee_id
        )
        if start is not None:
            query = query.filter(ScheduledShift.start_datetime >= start)
        if end is not None:
            query = query.filter(ScheduledShift.start_datetime < end)
        return query.order_by(ScheduledShift.start_datetime).all()

    def find_overlap(self, employee_id, start, end, exclude_id=None):
        query = db_session.query(ScheduledShift).filter(
            ScheduledShift.employee_id == employee_id,
            ScheduledShift.start_datetime < end,
            ScheduledShift.end_datetime > start,
        )
        if exclude_id is not None:
            query = query.filter(ScheduledShift.id != exclude_id)
        query = query.order_by(ScheduledShift.start_datetime)
        return query.with_for_update().first()

    def create(self, employee_id, start, end, hourly_rate):
        shift = ScheduledShift(
            employee_id=employee_id,
            start_datetime=start,
            end_datetime=end,
            hourly_rate_snapshot=hourly_rate,
        )
        db_session.add(shift)
        db_session.flush()
        return shift
