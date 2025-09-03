# book.py
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db, book_schema, books_schema
from app.jwt_extensions import limiter
from app.functions import (
	get_book_query_params, 
	book_filters_and_sorting,
	json_required)
'''
What this file contains :-
= Books CRUD
= Favourites CRUD
= Recover deleted books
'''
class Book_CR(Resource):
	@jwt_required()
	def get(self):
		from app.models.book import book_manager
		from app.extensions import books_schema

		params = get_book_query_params()
		filters, order_by = book_filters_and_sorting(params)

		query = book_manager.query.filter(*filters)

		if order_by:
			query = query.order_by(*order_by)

		pagination = query.paginate(
			page=params["page"], per_page=params["per_page"], error_out=False)
		
		if not pagination.items:
			abort(404, description="Book not found.")

		else:
			books =  books_schema.dump(pagination.items)

			return {
			'books': books,
			'page': pagination.page,
			'per_page': pagination.per_page,
			'total_items': pagination.total,
			'total_pages': pagination.pages
			}, 200

	@jwt_required()
	@json_required
	@limiter.limit("50 per day")
	def post(self, data):
		from app.extensions import book_schema
		errors = book_schema.validate(data)

		if errors:
			raise CustomBadRequest("Validation failed")

		else:
			title = data.get("title")
			author = data.get("author")
			genre = data.get("genre", None)

			normalized_title = title.lower().strip()

			if genre is not None:
				genre_normal = genre.lower().strip()
			else:
				genre_normal = None
				
			from app.models import book_manager

			del_check = book_manager.query.filter_by(
				user_id=get_jwt_identity()
				,is_deleted=True
				,normalized_title=normalized_title).first() 
			
			if not del_check:
				new_book = book_manager(
					title = title,
					author = author,
					normalized_title = normalized_title,
					user_id = get_jwt_identity(),
					is_deleted = False,
					genre = genre,
					genre_normal = genre_normal
				)

				try:
					db.session.add(new_book)
					db.session.commit()
					return book_schema.dump(new_book), 201
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e
			else:
				del_check.is_deleted = False
				try:
					db.session.commit()
					return {'message' : f"({del_check.title}) is added to the list."}
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e
					return {'message' : 'An error occured'}, 500

# JWT protected class to update, delete and get book by id.
class Book_RUD(Resource):
	@jwt_required()
	def get(self, id):
		from app.models.book import book_manager
		from app.extensions import book_schema

		current_user_id = get_jwt_identity()
		book_to_work = book_manager.query.filter_by(
			user_id=current_user_id, 
			id=id, 
			is_deleted = False
			).first()        
		
		if not book_to_work:
			abort(404, description="Book not found.")
		else:
			return (book_schema.dump(book_to_work)), 200

	@jwt_required()
	@json_required
	@limiter.limit("50 per day")
	def patch(self, data, id):
		from app.models.book import book_manager
		current_user_id = get_jwt_identity()
		
		book_tw = book_manager.query.filter_by(user_id=current_user_id, id=id).first()
		
		if not book_tw:
			abort(404, description="Book not found.")

		if 'title' in data and data['title'] is not None:
			book_tw.title = data['title']
			book_tw.normalized_title = data['title'].lower().strip()
		
		if 'author' in data and data['author'] is not None:
			book_tw.author = data['author']

		if 'genre' in data and data['genre'] is not None:
			book_tw.genre = data['genre']
			book_tw.genre_normal = data['genre'].lower().strip()

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
			raise e
			return {'message' : 'An error occured'}, 500

	@jwt_required()
	@limiter.limit("50 per day")
	def delete(self, id):
		current_user_id = get_jwt_identity()
		
		from app.models.book import book_manager
		book_tw = book_manager.query.filter_by(user_id=current_user_id, id=id).first()
		if not book_tw:
			abort(404, description="Book not found.")

		try:    
			book_tw.is_deleted = True
			book_tw.updated_at = datetime.utcnow()
			db.session.commit()
			return {"message" : "Deleted Successfully"}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			raise e
			return {'message' : 'An error occured'}, 500

class Book_reuse(Resource):
	@jwt_required()
	def get(self):
		page = request.args.get('page', 1, type=int)
		per_page = request.args.get('per_page', 5, type=int)

		from app.models.book import book_manager
		from app.extensions import books_schema
		
		current_user_id = get_jwt_identity()
		
		pagination = book_manager.query.filter(
			book_manager.user_id == get_jwt_identity(),
			book_manager.is_deleted == True
		).paginate(page=page, per_page=per_page, error_out=False)


		if not pagination.items:
			abort(404, description="Book not found.")

		else:
			books =  books_schema.dump(pagination.items)

			return {
			'del_books': books,
			'page': pagination.page,
			'per_page': pagination.per_page,
			'total_items': pagination.total,
			'total_pages': pagination.pages
			}, 200


class BookRecover(Resource):
	@jwt_required()
	def put(self, id):
		from app.models.book import book_manager
		current_user_id = get_jwt_identity()
		
		check = book_manager.query.filter(
			book_manager.user_id == current_user_id,
			book_manager.id == id).first()
		
		if not check:
			return {"message" : "Book not found"}, 404

		else:
			if check.is_deleted:
				try:
					check.is_deleted = False
					db.session.commit()
					return {'message' : 'Book recovered.'}, 200
				except SQLAlchemyError as e:
					db.session.rollback()
					return {'message' : 'An error occured.'}, 500
			else:
				return {'message' : 'Book is already recovered. No need to send another recovery request.'}, 200

class Book_Favourite_get(Resource):
	@jwt_required()
	def get(self):
		from app.models.book import book_manager
		from app.extensions import books_schema

		params = get_book_query_params() 
		filters, order_by = book_filters_and_sorting(params)

		filters.append(book_manager.favourite == True)
		
		query = book_manager.query.filter(*filters)

		if order_by:
			query = query..order_by(*order_by)

		pagination = query.paginate(
			page=params["page"], 
			per_page=params["per_page"], error_out=False)

		if not pagination.items:
			abort(404, description="Books not found.")

		else:
			books =  books_schema.dump(pagination.items)

			return {
			'favourite_books': books,
			'page': pagination.page,
			'per_page': pagination.per_page,
			'total_items': pagination.total,
			'total_pages': pagination.pages
			}, 200

class Book_Favourite_ud(Resource):
	@jwt_required()
	def put(self, id):
		from app.models.book import book_manager
		current_user_id = get_jwt_identity()
		
		check = book_manager.query.filter(
			book_manager.user_id == current_user_id,
			book_manager.id == id).first()
		
		if not check:
			return {"message" : "Book not found"}, 404

		else:
			if check.favourite:
				return {'message' : 'Book already added as favourite.'}, 404

			elif check.is_deleted:
				return {'message' : 'Book deleted. Restore to add as favourite.'}, 400 

			elif not check.favourite:
				try:
					check.favourite = True
					db.session.commit()
					return {'message' : 'Book added as favourite'}, 200
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e
					return {'message' : 'An error occured.'}, 500

	@jwt_required()
	def delete(self, id):
		from app.models.book import book_manager
		
		current_user_id = get_jwt_identity()

		check = book_manager.query.filter(
			book_manager.user_id == current_user_id,
			book_manager.id == id).first()
		
		if not check:
			return {"message" : "Book not found"}

		else:
			if check.is_deleted:
				return {'message' : 'Book already deleted. Head to /api/v1/recovery to restore.'}, 404

			elif check.favourite:
				try:
					check.favourite = False
					db.session.commit()
					return {'message' : 'Book removed from favourites.'}, 200
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e
					return {'message' : 'An error occured.'}, 500
