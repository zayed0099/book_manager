# authdb_manage.py
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
	UnivAuthorDB,
	BookAuthorLink)
from app.logging.setup_all import admin_logger
from app.functions import json_required

class AuthorUD(Resource):
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

		author = data.get("author", None)
		status = data.get("status", None)

		if (
			author is None 
			or status is None 
			or not isinstance(author, str) 
			or not isinstance(status, str)
		):
			return {"message" : "Author name is required in Str format."}, 400
		else:	
			author_normal = author.strip().lower()
			status_norm = status.strip().lower()

		accepted = ['active' , 'banned' , 'on_hold']

		query = UnivAuthorDB.query.filter(
			UnivAuthorDB.id == id).first()

		if not query:
			return {"message" : "No author Found."}, 404

		try:
			if author is not None:
				query.author = author
				query.author_normal = author_normal
			
			if status is not None:
				query.status = status_norm
				
			db.session.commit()
			admin_logger.info(
				f'{query.author}[id : {query.id}] data has been updated by admin[id : {get_jwt_identity()}]')
			return {'message' : 'Author data successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500

class AuthorCR(Resource):
	@jwt_required()
	@json_required
	@admin_required
	def get(data):
		pass
