from marshmallow import Schema, fields, validates, ValidationError

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

def validate_word_count(value):
    word_count = len(value.strip().split())
    if word_count > 100:
        raise ValidationError("Review must not exceed 100 words.")
    if word_count < 5:
        raise ValidationError("Review must be at least 5 words.")

class ReviewBookSchema(Schema):
	id = fields.Int(dump_only=True)
	review = fields.Str(required=True, validate=validate_word_count)
	rating = fields.Int(required=True)