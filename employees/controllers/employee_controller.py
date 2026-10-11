from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components.employee_component import EmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.employee_serializer import EmployeeOutputSchema

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
        employee = self.component_class().update_hourly_rate(
            employee_id,
            request.data,
        )
        data = EmployeeOutputSchema().dump(employee)
        return Response(data, status=status.HTTP_200_OK)
