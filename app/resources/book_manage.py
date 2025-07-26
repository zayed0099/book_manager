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
			from app.functions import (
				book_filters_and_sorting, 
				get_book_query_params)

			params = get_book_query_params()
			filters, order_by = book_filters_and_sorting(params)

			db_query = db.session.query(book_manager, Ratings_Reviews)\
			.join(Ratings_Reviews, Ratings_Reviews.user_id == book_manager.user_id)\
			.filter(*filters)

			if order_by:
				query = db_query.order_by(*order_by)

			pagination = db_query.paginate(
				page=params['page'], 
				per_page=params['per_page'], 
				error_out=False)
			
			if not pagination.items:
				abort(404, description="Book not found.")

			else:
				books_sep = [pair[0] for pair in pagination.items]
				reviews_sep = [pair[1] for pair in pagination.items]

				books = books_schema.dump(books_sep)
				reviews = review_schema.dump(reviews_sep, many=True)

				return {
				'book' : books,
				'review' : reviews,
				'page': pagination.page,
            	'per_page': pagination.per_page,
            	'total_items': pagination.total,
            	'total_pages': pagination.pages
				}, 200