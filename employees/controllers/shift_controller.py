from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from employees.components.shift_component import ShiftComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.shift_serializer import ShiftOutputSchema

class EmployeeShiftViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = ShiftComponent

    def list(self, request, employee_id=None):
        shifts = self.component_class().list_shifts(
            employee_id,
            request.query_params,
        )
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(shifts, request, view=self)
        data = ShiftOutputSchema(many=True).dump(page)
        return paginator.get_paginated_response(data)

    def create(self, request, employee_id=None):
        shift = self.component_class().create_shift(employee_id, request.data)
        data = ShiftOutputSchema().dump(shift)
        return Response(data, status=status.HTTP_201_CREATED)

class ScheduledShiftViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = ShiftComponent

    def retrieve(self, request, pk=None):
        shift = self.component_class().get_shift(int(pk))
        data = ShiftOutputSchema().dump(shift)
        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        shift = self.component_class().update_shift(int(pk), request.data)
        data = ShiftOutputSchema().dump(shift)
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        self.component_class().delete_shift(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

class ForecastedPayViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = ShiftComponent

    def forecast(self, request, employee_id=None):
        result = self.component_class().forecast_summary(
            employee_id,
            request.query_params,
        )
        return Response(result, status=status.HTTP_200_OK)
