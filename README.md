# Employee Hub API

A learning project built with Django REST Framework, SQLAlchemy `scoped_session`, and Marshmallow. Controllers inherit from DRF `ViewSet`; repositories run `db_session.query(...)`; components contain business rules.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/token/` | Get an authentication token |
| GET / POST | `/api/employees/` | List employees / create an employee |
| GET | `/api/employees/{employee_id}/` | Get one employee |
| PATCH | `/api/employees/{employee_id}/hourly-rate/` | Change current hourly rate |
| GET / POST | `/api/employees/{employee_id}/shifts/` | List / schedule shifts |
| GET / PATCH / DELETE | `/api/shifts/{shift_id}/` | Retrieve / edit times / delete a shift |
| GET | `/api/employees/{employee_id}/forecasted-pay/?from=YYYY-MM-DD&to=YYYY-MM-DD` | Summarize planned hours and pay for inclusive dates |

## Windows PowerShell setup

From the folder containing `manage.py`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Create a MySQL database named `employee_hub`, then put your password in `.env`. Initialize authentication tables and SQLAlchemy tables:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py init_sqlalchemy_db
python manage.py runserver
```

Get a token with `POST http://127.0.0.1:8000/api/token/` using the superuser username and password. Send it as `Authorization: Token YOUR_TOKEN`. Reads require authentication; writes require a staff user.

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
{"hourly_rate": "9.25"}
```

Every scheduled shift stores a snapshot of the employee's hourly rate at creation. Updating the employee rate affects new shifts only.

## Schedule a shift

`POST /api/employees/1/shifts/`

```json
{
  "start_datetime": "2026-10-12T09:00:00+03:00",
  "end_datetime": "2026-10-12T17:00:00+03:00"
}
```

Datetimes must include a timezone and use whole minutes. They are converted to UTC for storage. A shift must end after it starts, cannot exceed 24 hours, and cannot overlap another shift for the same employee. The employee row is locked while checking and creating the shift.

Optional inclusive date filters for listing:

`GET /api/employees/1/shifts/?from=2026-10-01&to=2026-10-31`

Forecast for an inclusive date range:

`GET /api/employees/1/forecasted-pay/?from=2026-10-01&to=2026-10-31`

Hours are calculated from shift duration in minutes. Pay uses the saved rate snapshot and is rounded to two decimal places.
