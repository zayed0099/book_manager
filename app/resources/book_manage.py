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

# A Class to show all or user query specific book review and ratings
class BookRatings(Resource):
	@jwt_required()
	def get(self, id=None):
		current_user_id = get_jwt_identity()
		
		from app.models.book import (book_manager,
			Ratings_Reviews)
		
		from app.extensions import (
			review_schema,
			book_schema,
			books_schema)

		if id:
			results = db.session.query(book_manager, Ratings_Reviews)\
			.join(Ratings_Reviews,
				and_( 
					Ratings_Reviews.user_id == book_manager.user_id,
					Ratings_Reviews.book_id == book_manager.id
					)
				)\
			.filter(
				book_manager.user_id == current_user_id,
				Ratings_Reviews.id == id)\
			.first()

			if not results:
				abort(404, description="Book not found.")

			else:
				book = book_schema.dump(results[0])
				review = review_schema.dump(results[1])

				return {
				'message' : 'The requested book and review is successfully retrieved.' ,
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
				'message' : 'Successfully retrieved all books for GET',
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
				db.session.commit()
				return {'message' : 'Review successfully deleted.' ,
					'deleted_book' : review_schema.dump(review_tw)}
			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 500

# tags post
class Tags(Resource):
	@jwt_required()
	@limiter.limit("50 per day")
	def post(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing Json in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

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

	# @jwt_required()
	# @limiter.limit("50 per day")
	# def get(self, review_id=None):
	# 	from app.models.book import review_tags
	# 	from app.extensions import tagschema

	# 	if review_id:
	# i am still not sure how to fully implement tagging+reviews, maybe i will have to 
	# wait till creating the frontend to grasp the concept fully

class BookListName(Resource):
	@jwt_required()
	@limiter.limit("10 per day")
	def post(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing Json in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		from app.extensions import listdataschema

		errors = listdataschema.validate(data)
		
		if errors:
			raise CustomBadRequest("Validation failed")

		listname_raw = data.get('list_name')
		listname = listname_raw.lower().strip()

		from app.models import ListOwner	
		
		try:
			new_list = ListOwner(
				list_name = listname_raw ,
				list_name_norm = list_name ,
				user_id = get_jwt_identity()
				)

			db.session.commit(new_list)
			return {'message' : 'List successfully created.'}, 200

		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500

	@jwt_required()
	@limiter.limit("5 per day")
	def put(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing Json in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		from app.extensions import booklistschema

		errors = booklistschema.validate(data)

		if errors:
			raise CustomBadRequest("Validation failed")

		list_name = data.get('list_name')
		list_name_norm = list_name.lower().strip()

		from app.models import ListOwner
		query = ListOwner.query.filter_by(list_name_norm=list_name_norm,
			is_deleted=False).first()

		if not query:
			return {'message' : 'No book list found with that name'}, 404

		if query.is_deleted:
			return {'message' : 'Recover the list first to change name'}, 409

		else:
			query.list_name = list_name
			query.list_name_norm = list_name_norm

			try:
				db.session.commit()
				return {'message' : 'List name successfully updated'}, 200
			except SQLAlchemyError as e:
				db.session.rollback()
				raise e
				return {'message' : 'An error occured'}, 500

	@jwt_required()
	@limiter.limit("5 per day")
	def delete(self, id):
		from app.models import ListOwner, ListBook 

		list_tw = ListOwner.query.filter_by(id=id,
			user_id = get_jwt_identity()
			).first()

		if not list_tw:
			abort(404, description="Book List not found.")

		if list_tw.is_deleted:
			return {'message' : 'The list is already deleted....'}, 409

		else:
			list_books = ListBook.query.filter_by(list_id=list_tw.id).all()

			try:
				list_tw.is_deleted = True
				list_tw.updated_at = datetime.utcnow()

				for book in list_books:
					book.is_list_deleted = True

				db.session.commit()
				return {'message' : 'List successfully deleted.'}, 200
			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 500
				
class CustomBookList(Resource):
	@jwt_required()
	@limiter.limit("50 per day")
	def post(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing Json in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		from app.extensions import booklistschema

		errors = booklistschema.validate(data)

		if errors:
			raise CustomBadRequest("Validation failed")		

		list_id = data.get('list_id')
		title = data.get('title')
		norm_title = title.lower().strip()
		author = data.get('author')
		genre = data.get('genre', None)
		status = data.get('status')

		from app.models import ListBook, ListOwner
		
		query = ListOwner.query.filter_by(list_id=list_id).first()

		if query.is_deleted:
			return {'message' : "The list is deleted. New books can't be added"}, 409

		else:
			try:
				new_book = ListBook(
					list_id = list_id,
					title = title,
					normalized_title = norm_title,
					author = author,
					genre = genre,
					status = status
					)

				db.session.commit(new_book)
				return {'message' : f'Book successfully added to list. List_id {list_id}'}, 200

			except SQLAlchemyError as e:
				db.session.rollback()
				return {'message' : 'An error occured'}, 500		

	@jwt_required()
	@limiter.limit("50 per day")
	def patch(self, id):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		from app.models import ListBook
		book_tw = ListBook.query.filter_by(id=id).first()

		if not book_tw:
			abort(404, description="Book not found.")

		if book_tw.is_list_deleted:
			return {'message' : 'The list is deleted. No change can be made now.'}, 409
			
		if 'title' in data and data['title'] is not None:
			book_tw.title = data['title']
			book_tw.normalized_title = data['title'].lower().strip()

		if 'author' in data and data['author'] is not None:
			book_tw.author = data['author']

		if 'genre' in data['genre'] is not None:
			book_tw.genre = data['genre']

		allowed = ['wishlist' , 'in_progress' , 'completed' , 'abandoned']

		if 'status' in data and data['status'] is not None:
			if data['status'] in allowed:
				book_tw.status = data['status']
			else:
				return {'message': f"Invalid status. Allowed values: {', '.join(allowed)}"}, 400

		try:
			book_tw.updated_at = datetime.utcnow()
			db.session.commit()
			return {
					"message": "Data updated Successfully",
					"book": {
						"title": book_tw.title,
						"author": book_tw.author,
						"genre": book_tw.genre ,
						"status" : book_tw.status,
						"updated_at" : book_tw.updated_at
					}
				}, 200

		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 404

	@jwt_required()
	@limiter.limit("50 per day")
	def delete(self, id):
		current_user_id = get_jwt_identity()
	
		from app.models import ListBook
		book_tw = ListBook.query.filter_by(id=id).first()
		
		if not book_tw:
			abort(404, description="Book not found.")

		if book_tw.is_list_deleted:
			return {'message' : 'The list is deleted. No change can be made now.'}, 409

		try:    
			db.session.delete(book_tw)
			db.session.commit()
			return {"message" : "Deleted Successfully"}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			raise e

	# @jwt_required()
	# def get(self, id=None):
	# 	if id is not None:
	# 		pass