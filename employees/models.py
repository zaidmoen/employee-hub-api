from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column

from employees.sqlalchemy_db import Base


class Employee(Base):
    __tablename__ = "employees"

    id = mapped_column(Integer, primary_key=True)
    first_name = mapped_column(String(100), nullable=False)
    last_name = mapped_column(String(100), nullable=False)
    email = mapped_column(String(254), nullable=False, unique=True, index=True)
    phone_number = mapped_column(String(30), nullable=False)
    hourly_rate = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )


class ScheduledShift(Base):
    __tablename__ = "scheduled_shifts"
    __table_args__ = (
        CheckConstraint("end_datetime > start_datetime", name="shift_end_after_start"),
        Index("shift_employee_start_idx", "employee_id", "start_datetime"),
    )

    id = mapped_column(Integer, primary_key=True)
    employee_id = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # MySQL DATETIME has no timezone so these values are stored as naive UTC
    start_datetime = mapped_column(DateTime(timezone=False), nullable=False)
    end_datetime = mapped_column(DateTime(timezone=False), nullable=False)
    hourly_rate_snapshot = mapped_column(Numeric(10, 2), nullable=False)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )


class Department(Base):
    __tablename__ = "departments"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(120), nullable=False, unique=True)
    code = mapped_column(String(20), nullable=False, unique=True)
    is_active = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )


class JobPosition(Base):
    __tablename__ = "job_positions"
    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "title",
            name="position_department_title_uq",
        ),
    )

    id = mapped_column(Integer, primary_key=True)
    department_id = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title = mapped_column(String(120), nullable=False)
    code = mapped_column(String(30), nullable=False, unique=True)
    is_active = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = mapped_column(Integer, primary_key=True)
    employee_id = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    employee_number = mapped_column(String(40), nullable=False, unique=True)
    department_id = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    position_id = mapped_column(
        Integer,
        ForeignKey("job_positions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    manager_id = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employment_status = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
    )
    hire_date = mapped_column(Date, nullable=True)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class EmployeeRateHistory(Base):
    __tablename__ = "employee_rate_history"
    __table_args__ = (
        Index("rate_history_employee_time_idx", "employee_id", "created_at"),
    )

    id = mapped_column(Integer, primary_key=True)
    employee_id = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    old_rate = mapped_column(Numeric(10, 2), nullable=False)
    new_rate = mapped_column(Numeric(10, 2), nullable=False)
    reason = mapped_column(String(255), nullable=True)
    changed_by = mapped_column(String(150), nullable=True)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        Index("attendance_employee_clock_idx", "employee_id", "clock_in"),
    )

    id = mapped_column(Integer, primary_key=True)
    employee_id = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shift_id = mapped_column(
        Integer,
        ForeignKey("scheduled_shifts.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    clock_in = mapped_column(DateTime(timezone=False), nullable=False)
    clock_out = mapped_column(DateTime(timezone=False), nullable=True)
    status = mapped_column(String(30), nullable=False, default="CLOCKED_IN")
    arrival_status = mapped_column(String(30), nullable=False, default="ON_TIME")
    worked_minutes = mapped_column(Integer, nullable=True)
    note = mapped_column(String(500), nullable=True)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class PayrollPeriod(Base):
    __tablename__ = "payroll_periods"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="payroll_end_after_start"),
        UniqueConstraint("start_date", "end_date", name="payroll_period_range_uq"),
    )

    id = mapped_column(Integer, primary_key=True)
    start_date = mapped_column(Date, nullable=False)
    end_date = mapped_column(Date, nullable=False)
    status = mapped_column(String(30), nullable=False, default="OPEN")
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )


class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    __table_args__ = (
        UniqueConstraint(
            "payroll_period_id",
            "employee_id",
            name="payroll_period_employee_uq",
        ),
    )

    id = mapped_column(Integer, primary_key=True)
    payroll_period_id = mapped_column(
        Integer,
        ForeignKey("payroll_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_id = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    regular_minutes = mapped_column(Integer, nullable=False, default=0)
    overtime_minutes = mapped_column(Integer, nullable=False, default=0)
    gross_pay = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("audit_entity_time_idx", "entity_type", "entity_id", "created_at"),
    )

    id = mapped_column(Integer, primary_key=True)
    actor = mapped_column(String(150), nullable=True)
    action = mapped_column(String(100), nullable=False)
    entity_type = mapped_column(String(80), nullable=False)
    entity_id = mapped_column(String(80), nullable=False)
    details = mapped_column(Text, nullable=True)
    created_at = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        nullable=False,
    )
