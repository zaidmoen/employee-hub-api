from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import mapped_column
from employees.sqlalchemy_db import Base

class Employee(Base):
    __tablename__ = "employees"
    id = mapped_column(Integer, primary_key=True)
    first_name = mapped_column(String(100), nullable=False)
    last_name = mapped_column(String(100), nullable=False)
    email = mapped_column(String(254), nullable=False, unique=True, index=True)
    phone_number = mapped_column(String(30), nullable=False)
    hourly_rate = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

class ScheduledShift(Base):
    __tablename__ = "scheduled_shifts"
    __table_args__ = (
        CheckConstraint("end_datetime > start_datetime", name="shift_end_after_start"),
        Index("shift_employee_start_idx", "employee_id", "start_datetime"),
    )
    id = mapped_column(Integer, primary_key=True)
    employee_id = mapped_column(Integer, ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False)
    # MySQL DATETIME has no timezone; these values are stored as naive UTC.
    start_datetime = mapped_column(DateTime(timezone=False), nullable=False)
    end_datetime = mapped_column(DateTime(timezone=False), nullable=False)
    hourly_rate_snapshot = mapped_column(Numeric(10, 2), nullable=False)
    created_at = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)
