from marshmallow import Schema, fields, validate, ValidationError


class ListDataSchema(Schema):
	id = fields.Int(dump_only=True)
	list_name = fields.Str(required=True, validate=validate.Length(min=1))

def validate_status(value):
	accepted = ['wishlist' , 'in_progress' , 'completed' , 'abandoned']
	check = value.strip().lower()

	if check not in accepted:
		raise ValidationError(f"Invalid status! Must be one of: {', '.join(accepted)}.")

def validate_audience(value):
	accepted = ['everyone', 'private']

	check = value.strip().lower()

	if check not in accepted:
		raise ValidationError(f"Invalid status! Must be one of: {', '.join(accepted)}.")

class BookListSchema(Schema):
	id = fields.Int(dump_only=True)
	list_id = fields.Int(required=True)
	title = fields.Str(required=True, validate=validate.Length(min=1))
	author = fields.Str(required=True, validate=validate.Length(min=1))
	genre = fields.Str(required=False)
	status = fields.Str(required=False, validate=validate_status, missing=None)
	audience = fields.Str(required=False, validate=validate_audience, missing=None)