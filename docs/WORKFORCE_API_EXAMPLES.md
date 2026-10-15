# Workforce API Examples

These examples assume the API is running locally at `http://127.0.0.1:8000/api/` and the request includes a valid authentication token.

## Create a department

`POST /api/departments/`

```json
{
  "name": "Engineering",
  "code": "ENG"
}
```

## Create a position

`POST /api/positions/`

```json
{
  "department_id": 1,
  "title": "Backend Developer",
  "code": "BE-DEV"
}
```

Positions can be filtered by department:

```text
GET /api/positions/?department_id=1
```

## Create or replace an employee profile

`PUT /api/employees/1/profile/`

```json
{
  "employee_number": "EMP-001",
  "department_id": 1,
  "position_id": 1,
  "manager_id": 2,
  "employment_status": "ACTIVE",
  "hire_date": "2026-10-01"
}
```

Read the profile with:

```text
GET /api/employees/1/profile/
```

## Change an hourly rate

`PATCH /api/employees/1/hourly-rate/`

```json
{
  "hourly_rate": "12.50",
  "reason": "performance review"
}
```

Every successful change creates a history entry.

```text
GET /api/employees/1/rate-history/
```

## Schedule a shift

`POST /api/employees/1/shifts/`

```json
{
  "start_datetime": "2026-10-20T09:00:00+03:00",
  "end_datetime": "2026-10-20T17:00:00+03:00"
}
```

## Clock in

`POST /api/shifts/1/clock-in/`

```json
{
  "clock_in": "2026-10-20T09:04:00+03:00"
}
```

A clock in within five minutes after the scheduled start is still classified as `ON_TIME`.

## Clock out

`POST /api/attendance/1/clock-out/`

```json
{
  "clock_out": "2026-10-20T17:30:00+03:00",
  "note": "release support"
}
```

The server calculates `worked_minutes` when clock out succeeds.

Employee attendance history is available at:

```text
GET /api/employees/1/attendance/
```

## Create a payroll period

`POST /api/payroll/periods/`

```json
{
  "start_date": "2026-10-01",
  "end_date": "2026-10-31"
}
```

## Calculate payroll

`POST /api/payroll/periods/1/calculate/`

The calculation uses completed attendance records inside the period. Work up to the scheduled shift duration is regular time. Work beyond the scheduled duration is overtime and is paid at 1.50 times the saved shift rate.

Read generated records with:

```text
GET /api/payroll/periods/1/records/
```

## Finalize payroll

`POST /api/payroll/periods/1/finalize/`

A payroll period must be calculated before it can be finalized. Finalized periods cannot be recalculated.

## Example workflow

```text
Create employee
    -> create department and position
    -> save employee profile
    -> schedule shift
    -> clock in
    -> clock out
    -> create payroll period
    -> calculate payroll
    -> review payroll records
    -> finalize payroll
```
