from decimal import Decimal
from marshmallow import Schema, ValidationError, fields, validate


class StrictMoneyField(fields.Decimal):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            raw_value = Decimal(str(value))
        except Exception:
            raw_value = None
        if raw_value is not None and raw_value.as_tuple().exponent < -2:
            raise ValidationError("Use no more than two decimal places.")
        return super()._deserialize(value, attr, data, **kwargs)

class EmployeeInputSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone_number = fields.String(required=True, validate=validate.Length(min=1, max=30))
    hourly_rate = StrictMoneyField(
        required=False,
        load_default=Decimal("0.00"),
        as_string=True,
        places=2,
        validate=validate.Range(min=Decimal("0.00"), max=Decimal("99999999.99")),
    )

class EmployeeOutputSchema(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    phone_number = fields.String()
    hourly_rate = fields.Decimal(as_string=True, places=2)

class EmployeeRateInputSchema(Schema):
    hourly_rate = StrictMoneyField(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(min=Decimal("0.00"), max=Decimal("99999999.99")),
    )
