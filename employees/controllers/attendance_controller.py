from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components.attendance_component import AttendanceComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.attendance_serializer import AttendanceOutputSchema


class EmployeeAttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = AttendanceComponent

    def list(self, request, employee_id=None):
        records = self.component_class().list_employee_attendance(employee_id)
        data = AttendanceOutputSchema(many=True).dump(records)
        return Response(data, status=status.HTTP_200_OK)


class ShiftAttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = AttendanceComponent

    def clock_in(self, request, shift_id=None):
        actor_username = getattr(request.user, "username", None)
        attendance = self.component_class().clock_in(
            shift_id,
            request.data,
            actor_username=actor_username,
        )
        data = AttendanceOutputSchema().dump(attendance)
        return Response(data, status=status.HTTP_201_CREATED)


class AttendanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = AttendanceComponent

    def retrieve(self, request, pk=None):
        attendance = self.component_class().get_attendance(pk)
        data = AttendanceOutputSchema().dump(attendance)
        return Response(data, status=status.HTTP_200_OK)

    def clock_out(self, request, pk=None):
        actor_username = getattr(request.user, "username", None)
        attendance = self.component_class().clock_out(
            pk,
            request.data,
            actor_username=actor_username,
        )
        data = AttendanceOutputSchema().dump(attendance)
        return Response(data, status=status.HTTP_200_OK)
