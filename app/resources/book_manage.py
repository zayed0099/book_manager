from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter

# A Class to show all or user query specific book review and ratings
class BookRatings(Resource):
	def get(self, book_id=None):
		current_user_id = get_jwt_identity()
		
		from app.models.book import (book_manager,
			Ratings_Reviews)
		
		from app.extensions import (
			review_schema,
			book_schema,
			books_schema)

		if book_id:
			results = db.session.query(book_manager, Ratings_Reviews)\
			.join(Ratings_Reviews, Ratings_Reviews.user_id == book_manager.user_id)\
			.filter(
				book_manager.user_id == current_user_id,
				Ratings_Reviews.book_id == book_id)\
			.first()

			if not results:
				abort(404, description="Book not found.")

			else:
				book = book_schema.dump(results[0])
				review = review_schema.dump(results[1])

				return {
				'book' : book,
				'review' : review
				}, 200

		else:
			pass