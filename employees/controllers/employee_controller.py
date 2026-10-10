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
        return Response(EmployeeOutputSchema(many=True).dump(employees), status=status.HTTP_200_OK)
    def create(self, request):
        employee = self.component_class().create_employee(request.data)
        return Response(EmployeeOutputSchema().dump(employee), status=status.HTTP_201_CREATED)
    def retrieve(self, request, pk=None):
        employee = self.component_class().get_employee(int(pk))
        return Response(EmployeeOutputSchema().dump(employee), status=status.HTTP_200_OK)

class EmployeeRateViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent
    def update_rate(self, request, employee_id=None):
        employee = self.component_class().update_hourly_rate(employee_id, request.data)
        return Response(EmployeeOutputSchema().dump(employee), status=status.HTTP_200_OK)
