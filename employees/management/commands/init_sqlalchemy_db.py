from django.core.management.base import BaseCommand

from employees.models import Employee, ScheduledShift  # noqa: F401
from employees.sqlalchemy_db import Base, engine

class Command(BaseCommand):
    help = "Create the SQLAlchemy employee and shift tables."
    def handle(self, *args, **options):
        Base.metadata.create_all(bind=engine)
        self.stdout.write(self.style.SUCCESS("SQLAlchemy tables are ready."))
