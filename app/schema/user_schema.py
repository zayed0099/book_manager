from marshmallow import Schema, fields, validate, ValidationError

def validate_role(value):
    valid = ['user' , 'admin' , 'system_admin']
    check = value.strip().lower()

    if check not in valid:
        raise ValidationError(f"Invalid role! Must be one of: {', '.join(valid)}.")

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    email = fields.Str(required=True, validate=validate.Length(min=1))
    role = fields.Str(required=False, validate=validate_role ,missing=None)

class AdminUserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)

class AdminUserSchema_min(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)
    is_banned = fields.Str(dump_only=True)