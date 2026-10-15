from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from employees.components.organization_component import OrganizationComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.organization_serializer import (
    DepartmentOutputSchema,
    EmployeeProfileOutputSchema,
    PositionOutputSchema,
)


class DepartmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = OrganizationComponent

    def list(self, request):
        departments = self.component_class().list_departments()
        data = DepartmentOutputSchema(many=True).dump(departments)
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        department = self.component_class().create_department(request.data)
        data = DepartmentOutputSchema().dump(department)
        return Response(data, status=status.HTTP_201_CREATED)


class PositionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = OrganizationComponent

    def list(self, request):
        raw_department_id = request.query_params.get("department_id")
        department_id = None
        if raw_department_id is not None:
            try:
                department_id = int(raw_department_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError({
                    "department_id": "department_id must be an integer."
                }) from exc

        positions = self.component_class().list_positions(department_id)
        data = PositionOutputSchema(many=True).dump(positions)
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        position = self.component_class().create_position(request.data)
        data = PositionOutputSchema().dump(position)
        return Response(data, status=status.HTTP_201_CREATED)


class EmployeeProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = OrganizationComponent

    def retrieve(self, request, employee_id=None):
        profile = self.component_class().get_employee_profile(employee_id)
        data = EmployeeProfileOutputSchema().dump(profile)
        return Response(data, status=status.HTTP_200_OK)

    def upsert(self, request, employee_id=None):
        profile = self.component_class().set_employee_profile(
            employee_id,
            request.data,
        )
        data = EmployeeProfileOutputSchema().dump(profile)
        return Response(data, status=status.HTTP_200_OK)
