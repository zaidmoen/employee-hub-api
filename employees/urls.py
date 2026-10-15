from django.urls import path

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
        "employees/<int:employee_id>/shifts/",
        EmployeeShiftViewSet.as_view({"get": "list", "post": "create"}),
        name="employee-shifts",
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
