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
	UnivPubDB,
	BookAuthorLink)
from app.logging.setup_all import admin_logger

class PublisherUD(Resource):
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

		publisher = data.get("publisher", None)
		status = data.get("status", None)

		if (
			publisher is None 
			status is None
			or not isinstance(publisher, str)
			or not isinstance(status, str)
		):
			return {"message" : "Publisher name/status is required in Str format."}, 400
		else:
			status_norm = status.strip().lower()
			publisher_normal = publisher.strip().lower()

		query = UnivPubDB.query.filter(
			UnivPubDB.id == id).first()

		if not query:
			return {"message" : "No publisher Found."}, 404
			
		try:
			if publisher is not None:
				query.publisher = publisher
				query.publisher_normal = publisher_normal
			
			if status is not None:
				query.status = status_norm

			db.session.commit()
			admin_logger.info(
				f'{query.publisher}[id : {query.id}] data has been updated by admin[id : {get_jwt_identity()}]')
			return {'message' : 'Publisher data successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500