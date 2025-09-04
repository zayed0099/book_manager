# pubdb_manage.py
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
	UnivCatDB,
	BookAuthorLink)
from app.logging.setup_all import admin_logger
from app.services import json_required

class CategoryUD(Resource):
	# to update a authors name in the db
	@jwt_required()
	@json_required
	@admin_required
	def patch(self, data, id):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		category = data.get("category", None)
		status = data.get("status", None)

		if (
			category is None 
			or status is None
			or not isinstance(category, str)
			or not isinstance(status, str)
		):
			return {"message" : "Category name/status is required in Str format."}, 400
		else:
			status_norm = status.strip().lower()
			category_normal = category.strip().lower()

		query = UnivCatDB.query.filter(
			UnivCatDB.id == id).first()

		if not query:
			return {"message" : "No category Found."}, 404
			
		try:
			if category is not None:
				query.category = category
				query.category_normal = category_normal
			
			if status is not None:
				query.status = status_norm

			db.session.commit()
			admin_logger.info(
				f'{query.category}[id : {query.id}] data has been updated by admin[id : {get_jwt_identity()}]')
			return {'message' : 'Category data successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500