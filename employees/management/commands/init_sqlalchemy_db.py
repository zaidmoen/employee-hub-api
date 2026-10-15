from django.core.management.base import BaseCommand

from employees.models import (  # noqa: F401
    AttendanceRecord,
    AuditLog,
    Department,
    Employee,
    EmployeeProfile,
    EmployeeRateHistory,
    JobPosition,
    PayrollPeriod,
    PayrollRecord,
    ScheduledShift,
)
from employees.sqlalchemy_db import Base, engine


class Command(BaseCommand):
    help = "Create all SQLAlchemy tables used by Employee Hub."

    def handle(self, *args, **options):
        Base.metadata.create_all(bind=engine)
        self.stdout.write(
            self.style.SUCCESS("Employee Hub SQLAlchemy tables are ready.")
        )
