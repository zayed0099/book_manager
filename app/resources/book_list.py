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

		user_id = get_jwt_identity()
		listname_raw = data.get('list_name')
		listname = listname_raw.lower().strip()

		from app.models import ListOwner	
		
		# checking how many list does the user have
		check = db.session.query(func.count(ListOwner.id)).filter(
			ListOwner.user_id == user_id).scalar()

		if check >= 3:
			return {'message' : 'Limit exceeded. A user can only have 3 book list'}, 400

		try:
			new_list = ListOwner(
				list_name = listname_raw ,
				list_name_norm = listname ,
				user_id = user_id
				)

			db.session.add(new_list)
			db.session.commit()
			return {'message' : 'List successfully created.'}, 201

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