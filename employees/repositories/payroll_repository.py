from employees.models import AuditLog, PayrollPeriod, PayrollRecord
from employees.sqlalchemy_db import db_session


class PayrollRepository:
    def list_periods(self):
        return (
            db_session.query(PayrollPeriod)
            .order_by(PayrollPeriod.start_date.desc(), PayrollPeriod.id.desc())
            .all()
        )

    def get_period(self, period_id, lock=False):
        query = db_session.query(PayrollPeriod).filter(PayrollPeriod.id == period_id)
        if lock:
            query = query.with_for_update()
        return query.first()

    def create_period(self, values):
        period = PayrollPeriod(**values)
        db_session.add(period)
        db_session.flush()
        return period

    def list_records(self, period_id):
        return (
            db_session.query(PayrollRecord)
            .filter(PayrollRecord.payroll_period_id == period_id)
            .order_by(PayrollRecord.employee_id)
            .all()
        )

    def delete_records(self, period_id):
        (
            db_session.query(PayrollRecord)
            .filter(PayrollRecord.payroll_period_id == period_id)
            .delete(synchronize_session=False)
        )

    def create_record(self, values):
        record = PayrollRecord(**values)
        db_session.add(record)
        db_session.flush()
        return record

    def add_audit_log(self, actor, action, period_id, details=None):
        entry = AuditLog(
            actor=actor,
            action=action,
            entity_type="payroll_period",
            entity_id=str(period_id),
            details=details,
        )
        db_session.add(entry)
        db_session.flush()
        return entry
