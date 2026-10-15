from marshmallow import EXCLUDE, Schema, fields, validate

from employees.serializers.shift_serializer import AwareDateTimeField


class ClockInInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    clock_in = AwareDateTimeField(required=True)
    note = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500),
    )


class ClockOutInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    clock_out = AwareDateTimeField(required=True)
    note = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=500),
    )


class AttendanceOutputSchema(Schema):
    id = fields.Integer()
    employee_id = fields.Integer()
    shift_id = fields.Integer()
    clock_in = AwareDateTimeField()
    clock_out = AwareDateTimeField(allow_none=True)
    status = fields.String()
    arrival_status = fields.String()
    worked_minutes = fields.Integer(allow_none=True)
    note = fields.String(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
