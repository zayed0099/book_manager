from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_ , and_

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter

# A Class to show all or user query specific book review and ratings
class BookRatings(Resource):
	@jwt_required()
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
			.join(Ratings_Reviews,
				and( 
					Ratings_Reviews.user_id == book_manager.user_id,
					Ratings_Reviews.book_id == book_manager.id
					)
				)\
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
			.join(Ratings_Reviews, 
				and_(
					Ratings_Reviews.user_id == book_manager.user_id,
					Ratings_Reviews.book_id == book_manager.id
					)
				)\
			.filter(*filters)

			if order_by:
				db_query = db_query.order_by(*order_by)

			pagination = db_query.paginate(
				page=params['page'], 
				per_page=params['per_page'], 
				error_out=False)
			
			if not pagination.items:
				abort(404, description="Book not found.")

			else:
				combined_data = []

				for book, review in pagination.items:
					combined_data.append({
						"book" : book_schema.dump(book),
						"review" : review_schema.dump(review)
						})

				return {
				'combined_data' : combined_data,
				'page': pagination.page,
				'per_page': pagination.per_page,
				'total_items': pagination.total,
				'total_pages': pagination.pages
				}, 200

	@jwt_required()
	@limiter.limit("50 per day")
	def post(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		from app.extensions import review_schema
		errors = review_schema.validate(data)

		if errors:
			raise CustomBadRequest("Validation failed")

		else:
			rating = data.get('rating')
			review = data.get('review')
			book_id = data.get('book_id')

			from app.models.book import Ratings_Reviews, book_manager
			new_review = Ratings_Reviews(
				rating = rating,
				review = review,
				user_id = get_jwt_identity(),
				book_id = book_id
				)

			from app.extensions import review_schema
			
			try:
				db.session.add(new_review)
				db.session.commit()
				return review_schema.dump(new_review), 201
			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 500


class BookRatings_UD(Resource):
	@jwt_required()
	@limiter.limit("50 per day")
	def patch(self, id):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing Json in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		rating = data.get('rating')
		review = data.get('review')

		from app.models.book import Ratings_Reviews
		
		review_tw = Ratings_Reviews.query.filter_by(
			user_id=get_jwt_identity(), 
			id=id).first()

		if not review_tw:
			abort(404, description="Review not found.")

		if any(key in data for key in ['rating', 'review']):
			if rating:
				review_tw['rating'] = rating

			if review:
				review_tw['review'] = review

			try:
				db.session.commit()
				return {
						"message": "Data updated Successfully",
						"review": {
							"rating": review_tw.rating,
							"review": review_tw.review
						}
					}, 200

			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 404

		else:
			return {'message' : 'ERROR! The data format is not correct.'}, 400

	@jwt_required()
	@limiter.limit("50 per day")
	def delete(self, id):
		current_user_id = get_jwt_identity()

		from app.models.book import Ratings_Reviews
		from app.extensions import review_schema
		review_tw = Ratings_Reviews.query.filter_by(
			user_id=get_jwt_identity(), 
			id=id).first()

		if not review_tw:
			abort(404, description='No review found.')

		else:
			try:
				db.session.delete(review_tw)
				return {'message' : 'Review successfully deleted.' ,
					'deleted_book' : review_schema.dump(review_tw)}
			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 404

