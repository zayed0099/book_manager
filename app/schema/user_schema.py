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

# user deleteion schema
def validate_word_count(value):
    word_count = len(value.strip().split())
    if word_count > 100:
        raise ValidationError("Review must not exceed 100 words.")
    if word_count < 5:
        raise ValidationError("Review must be at least 5 words.")

class DelRequestPOST(Schema):
    id = fields.Int(dump_only=True)
    notes = fields.Str(required=False, missing=None, validate=validate_word_count)

class DelRequestGET(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    role = fields.Str(dump_only=True)
    notes = fields.Str(dump_only=True)

