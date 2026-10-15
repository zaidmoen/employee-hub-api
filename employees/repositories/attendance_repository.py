from employees.models import AttendanceRecord, AuditLog
from employees.sqlalchemy_db import db_session


class AttendanceRepository:
    def get_by_id(self, attendance_id, lock=False):
        query = db_session.query(AttendanceRecord).filter(
            AttendanceRecord.id == attendance_id
        )
        if lock:
            query = query.with_for_update()
        return query.first()

    def get_by_shift(self, shift_id):
        return (
            db_session.query(AttendanceRecord)
            .filter(AttendanceRecord.shift_id == shift_id)
            .first()
        )

    def list_employee_records(self, employee_id):
        return (
            db_session.query(AttendanceRecord)
            .filter(AttendanceRecord.employee_id == employee_id)
            .order_by(AttendanceRecord.clock_in.desc())
            .all()
        )

    def get_completed_between(self, employee_id, start_datetime, end_datetime):
        return (
            db_session.query(AttendanceRecord)
            .filter(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.status == "COMPLETED",
                AttendanceRecord.clock_in >= start_datetime,
                AttendanceRecord.clock_in < end_datetime,
            )
            .order_by(AttendanceRecord.clock_in)
            .all()
        )

    def create(self, values):
        attendance = AttendanceRecord(**values)
        db_session.add(attendance)
        db_session.flush()
        return attendance

    def add_audit_log(self, actor, action, attendance):
        entry = AuditLog(
            actor=actor,
            action=action,
            entity_type="attendance",
            entity_id=str(attendance.id),
            details=f"employee={attendance.employee_id} shift={attendance.shift_id}",
        )
        db_session.add(entry)
        db_session.flush()
        return entry
