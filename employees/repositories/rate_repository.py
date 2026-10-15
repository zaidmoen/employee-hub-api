from employees.models import AuditLog, EmployeeRateHistory
from employees.sqlalchemy_db import db_session


class RateRepository:
    def create_history(self, values):
        history = EmployeeRateHistory(**values)
        db_session.add(history)
        db_session.flush()
        return history

    def list_history(self, employee_id):
        return (
            db_session.query(EmployeeRateHistory)
            .filter(EmployeeRateHistory.employee_id == employee_id)
            .order_by(EmployeeRateHistory.created_at.desc(), EmployeeRateHistory.id.desc())
            .all()
        )

    def add_audit_log(self, actor, employee_id, old_rate, new_rate, reason=None):
        details = f"hourly rate changed from {old_rate} to {new_rate}"
        if reason:
            details = f"{details} reason={reason}"

        entry = AuditLog(
            actor=actor,
            action="EMPLOYEE_RATE_UPDATED",
            entity_type="employee",
            entity_id=str(employee_id),
            details=details,
        )
        db_session.add(entry)
        db_session.flush()
        return entry
