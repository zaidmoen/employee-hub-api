from marshmallow import EXCLUDE, Schema, ValidationError, fields, validates_schema


class PayrollPeriodInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    @validates_schema
    def validate_range(self, values, **kwargs):
        if values["start_date"] > values["end_date"]:
            raise ValidationError({
                "end_date": "end_date must be on or after start_date."
            })


class PayrollPeriodOutputSchema(Schema):
    id = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()
    status = fields.String()
    created_at = fields.DateTime()


class PayrollRecordOutputSchema(Schema):
    id = fields.Integer()
    payroll_period_id = fields.Integer()
    employee_id = fields.Integer()
    regular_minutes = fields.Integer()
    overtime_minutes = fields.Integer()
    gross_pay = fields.Decimal(as_string=True, places=2)
    created_at = fields.DateTime()
