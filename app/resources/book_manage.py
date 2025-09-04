# book manage.py
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from datetime import datetime

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter
from app.services import json_required

# A Class to show all or user query specific book review and ratings
class BookRatings(Resource):
	@jwt_required()
	def get(self):
		from app.models import Ratings_Reviews
		from app.extensions import review_schema
		
		page = request.args.get("page", default=1, type=int),
		per_page = request.args.get("per_page", default=5, type=int)

		pagination = Ratings_Reviews.query.paginate(
			page=page, 
			per_page=per_page, 
			error_out=False)
		
		if not pagination.items:
			abort(404, description="Book not found.")

		return {
		'message' : 'Successfully retrieved all books for GET',
		'reviws' : pagination.items,
		'page': pagination.page,
		'per_page': pagination.per_page,
		'total_items': pagination.total,
		'total_pages': pagination.pages
		}, 200

	@jwt_required()
	@json_required
	@limiter.limit("50 per day")
	def post(self, data):
		from app.extensions import review_schema
		errors = review_schema.validate(data)

		if errors:
			raise CustomBadRequest("Validation failed")

		else:
			rating = data.get('rating')
			review = data.get('review')
			book_id = data.get('book_id')

			from app.models.book import Ratings_Reviews
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
	@json_required
	@limiter.limit("50 per day")
	def patch(self, data, id):
		rating = data.get('rating')
		review = data.get('review')

		from app.models import Ratings_Reviews
		
		review_tw = Ratings_Reviews.query.filter_by(
			user_id=get_jwt_identity(), 
			id=id).first()

		if not review_tw:
			abort(404, description="Review not found.")

		if 'rating' in data and data['rating'] is not None:
			review_tw.rating = rating

		if 'review' in data and data['review'] is not None:
			review_tw.review = review

		try:
			review_tw.updated_at = datetime.utcnow()
			db.session.commit()
			return {
					"message": "Data updated Successfully",
					"review": {
						"rating": review_tw.rating,
						"review": review_tw.review,
						"updated_at" : review_tw.updated_at
					}
				}, 200

		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500

	@jwt_required()
	@limiter.limit("50 per day")
	def delete(self, id):
		current_user_id = get_jwt_identity()

		from app.models import Ratings_Reviews
		from app.extensions import review_schema
		review_tw = Ratings_Reviews.query.filter_by(
			user_id=get_jwt_identity(), 
			id=id).first()

		if not review_tw:
			abort(404, description='No review found.')

		else:
			try:
				db.session.delete(review_tw)
				db.session.commit()
				return {'message' : 'Review successfully deleted.' ,
					'deleted_review' : review_schema.dump(review_tw)}
			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 500

# Tagging review
class Tags(Resource):
	@jwt_required()
	@json_required
	@limiter.limit("50 per day")
	def post(self, data):
		from app.models.book import review_tags
		from app.extensions import tagschema
		
		errors = tagschema.validate(data)
		
		if errors:
			raise CustomBadRequest("Validation failed")

		tags_raw = []
		tags = []
		tag1_raw = data.get('tag1')
		tag1 = tag1_raw.lower().strip()

		tag2_raw = data.get('tag2')
		tag2 = tag2_raw.lower().strip()

		review_id = data.get('review_id')
		
		tags_raw.append(tag1_raw)
		tags_raw.append(tag2_raw)
		tags.append(tag1)
		tags.append(tag2)

		try:
			for raw_tag, norm_tag in zip(tags_raw, tags):
				new_entry = review_tags(
					tag = raw_tag,
					normaliazed_tag = norm_tag,
					user_id = get_jwt_identity(),
					review_id = review_id
					)
				db.session.add(new_entry)

			db.session.commit()
			return {'message' : 'Tags added successfully for the review.'}, 201
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500

	@jwt_required()
	@limiter.limit("50 per day")
	def get(self):
		current_user_id = get_jwt_identity()

		from app.models.book import review_tags, Ratings_Reviews
		from app.extensions import gettagschema, review_schema

		page = request.args.get('page', 1, type=int)
		per_page = request.args.get('per_page', 20, type=int)

		user_query = request.args.get('tag')
		search_term = f"%{user_query}%"

		if user_query is not None:
			search_data = (db.session.query(review_tags, Ratings_Reviews)
			.join(Ratings_Reviews, 
				and_(
					Ratings_Reviews.user_id == review_tags.user_id,
					Ratings_Reviews.id == review_tags.review_id
					)
				)
			.filter(review_tags.normaliazed_tag.ilike(search_term)))
			# as ratings and reviews should be public
			
			pagination = search_data.paginate(
				page=page, 
				per_page=per_page, 
				error_out=False)
			
			if not pagination.items:
				abort(404, description="Book not found.")

			combined_data = []

			for tag, review in pagination.items:
				combined_data.append({
					"tag" : gettagschema.dump(tag),
					"review" : review_schema.dump(review)
					})

			return {
			'message' : 'Successfully retrieved all review for GET',
			'combined_data' : combined_data,
			'page': pagination.page,
			'per_page': pagination.per_page,
			'total_items': pagination.total,
			'total_pages': pagination.pages
			}, 200

		else:
			return {'message' : 'An error occured with the search query.'}, 400