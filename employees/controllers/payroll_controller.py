from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components.payroll_component import PayrollComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.payroll_serializer import (
    PayrollPeriodOutputSchema,
    PayrollRecordOutputSchema,
)


class PayrollPeriodViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = PayrollComponent

    def list(self, request):
        periods = self.component_class().list_periods()
        data = PayrollPeriodOutputSchema(many=True).dump(periods)
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request):
        actor_username = getattr(request.user, "username", None)
        period = self.component_class().create_period(
            request.data,
            actor_username=actor_username,
        )
        data = PayrollPeriodOutputSchema().dump(period)
        return Response(data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        period = self.component_class().get_period(pk)
        data = PayrollPeriodOutputSchema().dump(period)
        return Response(data, status=status.HTTP_200_OK)

    def records(self, request, pk=None):
        records = self.component_class().list_records(pk)
        data = PayrollRecordOutputSchema(many=True).dump(records)
        return Response(data, status=status.HTTP_200_OK)

    def calculate(self, request, pk=None):
        actor_username = getattr(request.user, "username", None)
        period, records = self.component_class().calculate_period(
            pk,
            actor_username=actor_username,
        )
        return Response(
            {
                "period": PayrollPeriodOutputSchema().dump(period),
                "records": PayrollRecordOutputSchema(many=True).dump(records),
            },
            status=status.HTTP_200_OK,
        )

    def finalize(self, request, pk=None):
        actor_username = getattr(request.user, "username", None)
        period = self.component_class().finalize_period(
            pk,
            actor_username=actor_username,
        )
        data = PayrollPeriodOutputSchema().dump(period)
        return Response(data, status=status.HTTP_200_OK)
