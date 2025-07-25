from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter

# A Class to show all or user query specific book review and ratings
class BookRatings(Resource):
	def get(self, book_id=None):
		current_user_id = get_jwt_identity()
		from app.models.book import book_manager
		from app.extensions import 
		from app.models.book import Ratings_Reviews

		if book_id:
			book_query = Ratings_Reviews.query.filter(
				Ratings_Reviews.user_id == current_user_id,
				Ratings_Reviews.book_id == book_id
				).first()

			if not book_review:
				abort(404, description="Book not found.")

			else:
				review = book_schema.dump(book_query)


		else:
			pass