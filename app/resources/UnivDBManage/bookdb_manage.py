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
from app.functions import update_field, json_required

class BookUD(Resource):
	# to update a authors name in the db
	@jwt_required()
	@json_required
	@admin_required
	def patch(self, id, data):
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
			return {"message" : "No book Found."}, 404

		update_field(book_tw, data, "title", "title")
		update_field(book_tw, data, "title", "normalized_title", lambda v: v.lower().strip())
		update_field(book_tw, data, "subtitle", "subtitle")
		update_field(book_tw, data, "description", "description")
		update_field(book_tw, data, "isbn1", "isbn1")
		update_field(book_tw, data, "isbn2", "isbn2")
		update_field(book_tw, data, "imagelink", "imagelink")
		update_field(book_tw, data, "pub_date", "pub_date")
		update_field(book_tw, data, "page_count", "page_count")
		update_field(book_tw, data, "language", "language")

		admin_user_id = get_jwt_identity()
		try:
			db.session.commit()
			admin_logger.info(
				f'{book_tw.title}[id : {book_tw.id}] data has been updated by admin[id : {admin_user_id}]')
			return {'message' : 'Book data successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500