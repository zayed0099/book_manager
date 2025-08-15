# admin.py
from flask_restful import Resource, request, abort
from datetime import datetime, timezone, timedelta
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from sqlalchemy import case, func

# Local Import
from app.extensions import db
from app.errors.handlers import CustomBadRequest
from app.jwt_extensions import (jwt, 
	limiter,
	admin_required,
	system_admin_required)

# This resource is registered in routes/admin.py
class AddBook(Resource):
	@jwt_required()
	@admin_required
	def post(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		title = data.get("title")
		normalized_title = title.strip().lower()

		subtitle = data.get("subtitle", None)

		author1 = data.get("author1")
		
		if isinstance(author1, str):
			author2_normal = author1.strip().lower()
		else:
			author2_normal = None

		author2 = data.get("author2", None)
		
		if isinstance(author2, str):
			author2_normal = author2.strip().lower()
		else:
			author2_normal = None

		author3 = data.get("author3", None)
		author4 = data.get("author4", None)
		author5 = data.get("author5", None)

		category1 = data.get("category1", None)
		
		if isinstance(category1, str):
			category1_normal = category1.strip().lower()
		else:
			category1_normal = None

		category2 = data.get("category2", None)
		
		if isinstance(category2, str):
			category2_normal = category2.strip().lower()
		else:
			category2_normal = None

		description = data.get("description", None)

		isbn1 = data.get("isbn1", None)
		isbn2 = data.get("isbn2", None)

		imagelink = data.get("imagelink")
		if imagelink is None:
			return {'message' : "Data w/o [imagelink] can't be accepted."}, 400

		publisher = data.get("publisher")
		
		if publisher is None:
			return {'message' : "Data w/o [publisher] can't be accepted."}, 400

		if isinstance(publisher, str):
			publisher_normal = publisher.strip().lower()
		else:
			publisher_normal = None 

		pub_date = data.get("pub_date", None)
		page_count = data.get("page_count", None)
		language = data.get("language", "en")

		from app.models import UnivBookDB

		new_book = UnivBookDB(
			title = title,
			normalized_title = normalized_title,
			subtitle = subtitle,
			author1 = author1,
			author1_normal = author1_normal,
			author2 = author2,
			author2_normal = author2_normal,
			author3 = author3,
			author4 = author4,
			author5 = author5,
			category1 = category1,
			category1_normal = category1_normal,
			category2 = category2,
			category2_normal = category2_normal,
			description = description,
			isbn1 = isbn1,
			isbn2 = isbn2,
			imagelink = imagelink,
			pub_date = pub_date,
			page_count = page_count,
			language = language
			)

		try:
			db.session.add(new_book)
			db.session.commit()
			return {'message' : 'Book successfully added'}, 201
		except SQLAlchemyError as e:
			db.session.rollback()
			raise e
			return {'message' : 'An error occured'}, 500

