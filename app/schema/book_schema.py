from marshmallow import Schema, fields, validate, ValidationError

# function for checking book status
def validate_status(value):
	accepted = ['wishlist' , 'in_progress' , 'completed' , 'abandoned']
	check = value.strip().lower()

	if check not in accepted:
		raise ValidationError(f"Invalid status! Must be one of: {', '.join(accepted)}.")

class BookSchema(Schema):
	id = fields.Int(dump_only=True)
	title = fields.Str(required=True, validate=validate.Length(min=1))
	author = fields.Str(required=True, validate=validate.Length(min=1))
	genre = fields.Str(required=False)
	status = fields.Str(required=False, validate=validate_status, missing=None) 
	updated_at = fields.Str(required=False, missing=None)
	'''missing=None , so even if the user doesnt sends a status, it wont
	throw an error and use the db default, status=wishlist'''

class AdminBookSchema(Schema):
	id = fields.Int(dump_only=True)
	title = fields.Str(dump_only=True)
	author = fields.Str(dump_only=True)
	genre = fields.Str(dump_only=True)
	is_deleted = fields.Bool(dump_only=True)
	favourite = fields.Bool(dump_only=True)
	user_id = fields.Int(dump_only=True)
	status = fields.Str(dump_only=True)

# Functions to validate word length and rating
def validate_word_count(value):
	word_count = len(value.strip().split())
	if word_count > 100:
		raise ValidationError("Review must not exceed 100 words.")
	if word_count < 5:
		raise ValidationError("Review must be at least 5 words.")

def validate_rating(value):
	if value > 10:
		raise ValidationError("rating must be between (1-10)")
	elif value < 1:
		raise ValidationError("rating must be between (1-10)")

# Schema for review
class ReviewBookSchema(Schema):
	id = fields.Int(dump_only=True)
	review = fields.Str(required=True, validate=validate_word_count)
	rating = fields.Int(required=True, validate=validate_rating)
	book_id = fields.Int(required=True)

# Schema for tags
class TagSchema(Schema):
	id = fields.Int(dump_only=True)
	tag1 = fields.Str(required=True, validate=validate.Length(min=3))
	tag2 = fields.Str(required=True, validate=validate.Length(min=3))
	review_id = fields.Int(required=True)


# Schema for Custom list