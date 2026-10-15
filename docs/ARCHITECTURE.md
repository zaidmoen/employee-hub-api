# Employee Hub Architecture

Employee Hub is organized as a small modular workforce management backend. The project keeps the original Django REST Framework entry point while using SQLAlchemy for the domain database and Marshmallow for request and response schemas.

## Request flow

```text
HTTP request
    |
    v
Controller / ViewSet
    |
    v
Component
    |
    v
Repository
    |
    v
SQLAlchemy models
    |
    v
Database
```

Controllers translate HTTP requests and responses. Components own business rules. Repositories own database queries. Marshmallow schemas validate external data before it reaches business logic.

## Workforce modules

### Employees

The employee module keeps basic identity and the current hourly rate. Existing employee endpoints remain compatible with the original project.

### Organization

Organization data is stored separately from the core employee row so the original employee table does not need new workforce columns.

- `Department` groups employees by business area.
- `JobPosition` belongs to a department.
- `EmployeeProfile` stores employee number, department, position, manager, employment status, and hire date.
- Manager references point back to the employee table.

Important rules:

- An employee cannot be their own manager.
- A position must belong to the selected department.
- Employee numbers are unique.
- Department and position codes are normalized to uppercase.

### Rate history

`Employee.hourly_rate` remains the current rate used by existing code. Every rate update also creates an `EmployeeRateHistory` row containing the old rate, new rate, optional reason, actor, and timestamp.

The rate update and history insert are committed in the same database transaction. An audit entry is written at the same time.

### Scheduling

The existing scheduling module remains responsible for planned work. It validates timezone-aware input, prevents overlapping shifts, limits a shift to 24 hours, and stores the hourly rate snapshot used for that shift.

The snapshot is important because a later rate change should not rewrite historical shift economics.

### Attendance

Attendance is linked one-to-one with a scheduled shift.

Clock in rules include:

- No duplicate attendance for the same shift.
- Clock in cannot happen after the scheduled shift has ended.
- Clock in cannot happen more than two hours before the scheduled start.
- Arrival is classified as `EARLY`, `ON_TIME`, or `LATE`.

Clock out rules include:

- Clock out must be after clock in.
- A completed attendance record cannot be clocked out again.
- An attendance duration cannot exceed 24 hours.
- Worked minutes are calculated when the employee clocks out.

### Payroll

Payroll uses completed attendance rather than planned shifts.

A payroll period moves through these states:

```text
OPEN -> CALCULATED -> FINALIZED
```

Calculation uses each shift's saved hourly rate snapshot.

```text
regular minutes = min(worked minutes, scheduled minutes)
overtime minutes = max(worked minutes - scheduled minutes, 0)
regular pay = regular hours * shift rate
overtime pay = overtime hours * shift rate * 1.50
```

Recalculating a non-finalized period replaces its generated payroll records. Finalized periods cannot be recalculated.

### Audit log

Important workforce actions create `AuditLog` rows. Current audit coverage includes hourly-rate changes, clock in, clock out, payroll period creation, payroll calculation, and payroll finalization.

## Transaction boundaries

Components own transaction boundaries because they know which business changes must succeed or fail together.

Examples:

- Rate update + rate history + audit log
- Clock in + attendance row + audit log
- Payroll calculation + payroll records + payroll status + audit log

Repositories never call `commit()` themselves. This keeps database writes composable inside a business operation.

## Database initialization

The project currently uses SQLAlchemy `Base.metadata.create_all()` through:

```powershell
python manage.py init_sqlalchemy_db
```

This creates missing tables. It is not a replacement for a production migration system. If this project grows further, Alembic would be the natural next step for versioned schema migrations.

## Suggested next modules

The current structure is ready for additional modules without changing the architecture. Good next additions are leave requests, shift swaps, notifications, role-based domain permissions, payroll deductions and bonuses, and background jobs for operational events.
