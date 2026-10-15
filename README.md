# Employee Hub API

A workforce management backend built with Django REST Framework, SQLAlchemy, and Marshmallow.

The project started as an employee and shift API and now includes organization structure, employee rate history, attendance tracking, payroll calculation, and audit logging while keeping the same layered architecture.

## Architecture

```text
Controller / ViewSet
        ↓
Component / business rules
        ↓
Repository / database access
        ↓
SQLAlchemy models
        ↓
Database
```

Controllers handle HTTP concerns. Components contain business rules and transaction boundaries. Repositories own SQLAlchemy queries. Marshmallow schemas validate input and serialize output.

More detail is available in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Main features

- Employee creation and retrieval
- Token authentication
- Admin-only writes
- Employee organization profiles
- Departments and job positions
- Manager hierarchy
- Hourly rate history with audit trail
- Shift scheduling with overlap protection
- Timezone-aware shift validation
- Forecasted pay from scheduled shifts
- Employee clock in and clock out
- Early, on-time, and late arrival classification
- Actual worked-minute calculation
- Payroll periods and payroll records
- Regular and overtime pay calculation
- Payroll finalization
- Audit logging for important workforce actions

## Core endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/token/` | Get an authentication token |
| GET / POST | `/api/employees/` | List employees / create an employee |
| GET | `/api/employees/{employee_id}/` | Get one employee |
| GET / PUT | `/api/employees/{employee_id}/profile/` | Read / save workforce profile |
| PATCH | `/api/employees/{employee_id}/hourly-rate/` | Change current hourly rate |
| GET | `/api/employees/{employee_id}/rate-history/` | Read rate changes |
| GET / POST | `/api/employees/{employee_id}/shifts/` | List / schedule shifts |
| GET / PATCH / DELETE | `/api/shifts/{shift_id}/` | Retrieve / edit / delete a shift |
| GET | `/api/employees/{employee_id}/forecasted-pay/` | Forecast scheduled pay |
| GET / POST | `/api/departments/` | List / create departments |
| GET / POST | `/api/positions/` | List / create job positions |
| POST | `/api/shifts/{shift_id}/clock-in/` | Clock in for a scheduled shift |
| POST | `/api/attendance/{attendance_id}/clock-out/` | Clock out and calculate worked minutes |
| GET | `/api/employees/{employee_id}/attendance/` | Employee attendance history |
| GET / POST | `/api/payroll/periods/` | List / create payroll periods |
| POST | `/api/payroll/periods/{period_id}/calculate/` | Calculate payroll from attendance |
| GET | `/api/payroll/periods/{period_id}/records/` | Read generated payroll records |
| POST | `/api/payroll/periods/{period_id}/finalize/` | Finalize calculated payroll |

Request examples are available in [`docs/WORKFORCE_API_EXAMPLES.md`](docs/WORKFORCE_API_EXAMPLES.md).

## Windows PowerShell setup

From the folder containing `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Create a MySQL database named `employee_hub`, then put your database connection in `.env`.

Initialize Django authentication tables and SQLAlchemy domain tables:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py init_sqlalchemy_db
python manage.py runserver
```

Get a token with `POST http://127.0.0.1:8000/api/token/` using the superuser username and password.

Send the token with requests:

```text
Authorization: Token YOUR_TOKEN
```

Reads require authentication. Writes require a staff user.

## Create an employee

`POST /api/employees/`

```json
{
  "first_name": "Lina",
  "last_name": "Khalil",
  "email": "lina@example.com",
  "phone_number": "0599000000",
  "hourly_rate": "8.50"
}
```

## Update hourly rate

`PATCH /api/employees/1/hourly-rate/`

```json
{
  "hourly_rate": "9.25",
  "reason": "performance review"
}
```

Every rate change stores the previous rate, new rate, optional reason, authenticated actor, and timestamp.

Every scheduled shift stores a snapshot of the employee's hourly rate at creation. Updating the employee rate affects new shifts only.

## Schedule a shift

`POST /api/employees/1/shifts/`

```json
{
  "start_datetime": "2026-10-20T09:00:00+03:00",
  "end_datetime": "2026-10-20T17:00:00+03:00"
}
```

Shift datetimes must include a timezone and use whole minutes. They are converted to UTC for storage.

A shift:

- must end after it starts
- cannot exceed 24 hours
- cannot overlap another shift for the same employee

The employee row is locked while checking and creating the shift.

Optional inclusive date filters for listing:

```text
GET /api/employees/1/shifts/?from=2026-10-01&to=2026-10-31&page=1
```

Forecast for an inclusive date range:

```text
GET /api/employees/1/forecasted-pay/?from=2026-10-01&to=2026-10-31
```

## Attendance and payroll

Scheduled pay and actual pay are intentionally separate.

```text
Scheduled Shift
      ↓
Clock In
      ↓
Attendance Record
      ↓
Clock Out
      ↓
Worked Minutes
      ↓
Payroll Calculation
```

Payroll calculation uses completed attendance records and the hourly rate snapshot saved on each shift.

Regular work is paid at the shift rate. Time worked beyond the scheduled shift duration is treated as overtime at `1.50x` the shift rate.

A payroll period follows:

```text
OPEN -> CALCULATED -> FINALIZED
```

A finalized payroll period cannot be recalculated.

## Database note

`python manage.py init_sqlalchemy_db` uses SQLAlchemy `create_all()` to create missing tables. This is suitable for the current learning project, but it does not provide versioned schema migrations.

For a production-style next step, add Alembic before making destructive or complex schema changes.
