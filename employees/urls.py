from django.urls import path

from employees.controllers.attendance_controller import (
    AttendanceViewSet,
    EmployeeAttendanceViewSet,
    ShiftAttendanceViewSet,
)
from employees.controllers.employee_controller import (
    EmployeeRateViewSet,
    EmployeeViewSet,
)
from employees.controllers.organization_controller import (
    DepartmentViewSet,
    EmployeeProfileViewSet,
    PositionViewSet,
)
from employees.controllers.shift_controller import (
    EmployeeShiftViewSet,
    ForecastedPayViewSet,
    ScheduledShiftViewSet,
)

# Keep URLs explicit so each HTTP method clearly maps to a ViewSet action.
urlpatterns = [
    path(
        "employees/",
        EmployeeViewSet.as_view({"get": "list", "post": "create"}),
        name="employee-list",
    ),
    path(
        "employees/<int:pk>/",
        EmployeeViewSet.as_view({"get": "retrieve"}),
        name="employee-detail",
    ),
    path(
        "employees/<int:employee_id>/profile/",
        EmployeeProfileViewSet.as_view({"get": "retrieve", "put": "upsert"}),
        name="employee-profile",
    ),
    path(
        "employees/<int:employee_id>/hourly-rate/",
        EmployeeRateViewSet.as_view({"patch": "update_rate"}),
        name="employee-hourly-rate",
    ),
    path(
        "employees/<int:employee_id>/rate-history/",
        EmployeeRateViewSet.as_view({"get": "history"}),
        name="employee-rate-history",
    ),
    path(
        "employees/<int:employee_id>/shifts/",
        EmployeeShiftViewSet.as_view({"get": "list", "post": "create"}),
        name="employee-shifts",
    ),
    path(
        "employees/<int:employee_id>/attendance/",
        EmployeeAttendanceViewSet.as_view({"get": "list"}),
        name="employee-attendance",
    ),
    path(
        "shifts/<int:pk>/",
        ScheduledShiftViewSet.as_view({
            "get": "retrieve",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="scheduled-shift-detail",
    ),
    path(
        "shifts/<int:shift_id>/clock-in/",
        ShiftAttendanceViewSet.as_view({"post": "clock_in"}),
        name="shift-clock-in",
    ),
    path(
        "attendance/<int:pk>/",
        AttendanceViewSet.as_view({"get": "retrieve"}),
        name="attendance-detail",
    ),
    path(
        "attendance/<int:pk>/clock-out/",
        AttendanceViewSet.as_view({"post": "clock_out"}),
        name="attendance-clock-out",
    ),
    path(
        "employees/<int:employee_id>/forecasted-pay/",
        ForecastedPayViewSet.as_view({"get": "forecast"}),
        name="employee-forecasted-pay",
    ),
    path(
        "departments/",
        DepartmentViewSet.as_view({"get": "list", "post": "create"}),
        name="department-list",
    ),
    path(
        "positions/",
        PositionViewSet.as_view({"get": "list", "post": "create"}),
        name="position-list",
    ),
]
