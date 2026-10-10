from marshmallow import ValidationError as MarshmallowValidationError
from rest_framework.exceptions import ValidationError

def load_schema(schema, data):
    try:
        return schema.load(data)
    except MarshmallowValidationError as exc:
        raise ValidationError(exc.messages) from exc
