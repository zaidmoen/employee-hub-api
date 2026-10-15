from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components.employee_component import EmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.employee_serializer import EmployeeOutputSchema
from employees.serializers.rate_serializer import EmployeeRateHistoryOutputSchema


class EmployeeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent

    def list(self, request):
        employees = self.component_class().list_employees()
        data = EmployeeOutputSchema(many=True).dump(employees)
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        employee = self.component_class().create_employee(request.data)
        data = EmployeeOutputSchema().dump(employee)
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        employee = self.component_class().get_employee(int(pk))
        data = EmployeeOutputSchema().dump(employee)
        return Response(data, status=status.HTTP_200_OK)


class EmployeeRateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent

    def update_rate(self, request, employee_id=None):
        actor_username = getattr(request.user, "username", None)
        employee = self.component_class().update_hourly_rate(
            employee_id,
            request.data,
            actor_username=actor_username,
        )
        data = EmployeeOutputSchema().dump(employee)
        return Response(data, status=status.HTTP_200_OK)

    def history(self, request, employee_id=None):
        entries = self.component_class().list_rate_history(employee_id)
        data = EmployeeRateHistoryOutputSchema(many=True).dump(entries)
        return Response(data, status=status.HTTP_200_OK)
