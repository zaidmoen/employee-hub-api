from decimal import Decimal

from marshmallow import EXCLUDE, Schema, fields, validate

from employees.serializers.employee_serializer import StrictMoneyField


class EmployeeRateChangeInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    hourly_rate = StrictMoneyField(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(
            min=Decimal("0.00"),
            max=Decimal("99999999.99"),
        ),
    )
    reason = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
    )


class EmployeeRateHistoryOutputSchema(Schema):
    id = fields.Integer()
    employee_id = fields.Integer()
    old_rate = fields.Decimal(as_string=True, places=2)
    new_rate = fields.Decimal(as_string=True, places=2)
    reason = fields.String(allow_none=True)
    changed_by = fields.String(allow_none=True)
    created_at = fields.DateTime()
