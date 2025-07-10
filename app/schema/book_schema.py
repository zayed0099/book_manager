from marshmallow import Schema, fields, validate

class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    author = fields.Str(required=True, validate=validate.Length(min=1))
    genre = fields.Str(required=False)

class AdminBookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    author = fields.Str(dump_only=True)
    genre = fields.Str(dump_only=True)
    is_deleted = fields.Bool(dump_only=True)
    favourite = fields.Bool(dump_only=True)
    user_id = fields.Int(dump_only=True)
