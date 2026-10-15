from marshmallow import EXCLUDE, Schema, fields, validate


EMPLOYMENT_STATUSES = (
    "ACTIVE",
    "ON_LEAVE",
    "SUSPENDED",
    "TERMINATED",
)


class DepartmentInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    code = fields.String(required=True, validate=validate.Length(min=2, max=20))


class DepartmentOutputSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    code = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()


class PositionInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    department_id = fields.Integer(required=True, strict=True)
    title = fields.String(required=True, validate=validate.Length(min=2, max=120))
    code = fields.String(required=True, validate=validate.Length(min=2, max=30))


class PositionOutputSchema(Schema):
    id = fields.Integer()
    department_id = fields.Integer()
    title = fields.String()
    code = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()


class EmployeeProfileInputSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    employee_number = fields.String(
        required=True,
        validate=validate.Length(min=2, max=40),
    )
    department_id = fields.Integer(required=False, allow_none=True, strict=True)
    position_id = fields.Integer(required=False, allow_none=True, strict=True)
    manager_id = fields.Integer(required=False, allow_none=True, strict=True)
    employment_status = fields.String(
        required=False,
        load_default="ACTIVE",
        validate=validate.OneOf(EMPLOYMENT_STATUSES),
    )
    hire_date = fields.Date(required=False, allow_none=True)


class EmployeeProfileOutputSchema(Schema):
    id = fields.Integer()
    employee_id = fields.Integer()
    employee_number = fields.String()
    department_id = fields.Integer(allow_none=True)
    position_id = fields.Integer(allow_none=True)
    manager_id = fields.Integer(allow_none=True)
    employment_status = fields.String()
    hire_date = fields.Date(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
