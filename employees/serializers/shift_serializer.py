from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from marshmallow import EXCLUDE, Schema, ValidationError, fields, validates_schema

def to_utc_naive(value):
    """Convert an aware datetime to naive UTC for MySQL DATETIME."""
    return value.astimezone(timezone.utc).replace(tzinfo=None)

def as_utc_aware(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

class AwareDateTimeField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise self.make_error("invalid")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise self.make_error("invalid") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValidationError("Datetime must include a timezone, such as Z or +03:00.")
        if parsed.second or parsed.microsecond:
            raise ValidationError("Shift times must use whole minutes; seconds must be 00.")
        return parsed.astimezone(timezone.utc)
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return as_utc_aware(value).isoformat(timespec="seconds").replace("+00:00", "Z")

class ShiftInputSchema(Schema):
    start_datetime = AwareDateTimeField(required=True)
    end_datetime = AwareDateTimeField(required=True)

class ShiftUpdateInputSchema(Schema):
    start_datetime = AwareDateTimeField(required=False)
    end_datetime = AwareDateTimeField(required=False)
    @validates_schema
    def require_a_time(self, values, **kwargs):
        if not values:
            raise ValidationError({"detail": "Provide a start_datetime or end_datetime."})

class ShiftOutputSchema(Schema):
    id = fields.Integer()
    employee_id = fields.Integer()
    start_datetime = AwareDateTimeField()
    end_datetime = AwareDateTimeField()
    hourly_rate = fields.Decimal(attribute="hourly_rate_snapshot", as_string=True, places=2)
    scheduled_hours = fields.Method("get_scheduled_hours")
    forecasted_pay = fields.Method("get_forecasted_pay")
    @staticmethod
    def duration_hours(shift):
        start, end = as_utc_aware(shift.start_datetime), as_utc_aware(shift.end_datetime)
        minutes = Decimal(str(int((end - start).total_seconds() // 60)))
        return minutes / Decimal("60")
    def get_scheduled_hours(self, shift):
        return f"{self.duration_hours(shift):.2f}"
    def get_forecasted_pay(self, shift):
        pay = self.duration_hours(shift) * shift.hourly_rate_snapshot
        return f"{pay.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"

class ShiftListQuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    from_date = fields.Date(data_key="from", required=False)
    to_date = fields.Date(data_key="to", required=False)
    @validates_schema
    def validate_range(self, values, **kwargs):
        if values.get("from_date") and values.get("to_date") and values["from_date"] > values["to_date"]:
            raise ValidationError({"detail": "'from' must be on or before 'to'."})

class ForecastQuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    from_date = fields.Date(data_key="from", required=True)
    to_date = fields.Date(data_key="to", required=True)
    @validates_schema
    def validate_range(self, values, **kwargs):
        if values["from_date"] > values["to_date"]:
            raise ValidationError({"detail": "'from' must be on or before 'to'."})
