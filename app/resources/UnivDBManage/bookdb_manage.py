# bookdb_manage.py
from flask_restful import Resource, request, abort
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

# Local Imports
from app.extensions import db
from app.errors.handlers import CustomBadRequest
from app.jwt_extensions import (
	jwt, 
	limiter,
	admin_required,
	system_admin_required)
from app.models import ( 
	UnivBookDB)
from app.logging.setup_all import admin_logger

def set_field(obj, data, key, attr, transform=lambda x:x):
	value = data.get(key)
	if value is not None:
		setattr(obj, attr, transform(value))


class BookUD(Resource):
	# to update a authors name in the db
	@jwt_required()
	@admin_required
	def patch(self, id):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		title = data.get("title", None)
		subtitle = data.get("subtitle", None)
		description = data.get("description", None)
		isbn1 = data.get("isbn1", None)
		isbn2 = data.get("isbn2", None)

		imagelink = data.get("imagelink", None)
		pub_date = data.get("pub_date", None)
		page_count = data.get("page_count", None)
		language = data.get("language", None)

		book_tw = UnivBookDB.query.filter(
			UnivBookDB.id == id).first()

		if not book_tw:
			return {"message" : "No publisher Found."}, 404

		set_field(book_tw, data, "title", "title")
		set_field(book_tw, data, "title", "normalized_title", lambda v: v.lower().strip())
		set_field(book_tw, data, "description", "description")
		set_field(book_tw, data, "description", "description")
		set_field(book_tw, data, "isbn1", "isbn1")
		set_field(book_tw, data, "isbn2", "isbn2")
		set_field(book_tw, data, "imagelink", "imagelink")
		set_field(book_tw, data, "pub_date", "pub_date")
		set_field(book_tw, data, "page_count", "page_count")
		set_field(book_tw, data, "language", "language")

		admin_user_id = get_jwt_identity()
		try:
			db.session.commit()
			admin_logger.info(
				f'{book_tw.title}[id : {book_tw.id}] data has been updated by admin[id : {admin_user_id}]')
			return {'message' : 'Book data successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500