# authdb_manage.py
from flask_restful import Resource, request, abort
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
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

class AuthorUD(Resource):
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

		author = data.get("author", None)
		author_normal = author.strip().lower()

		if author is None and not isinstance(author, str):
			return {"message" : "Author name is required in Str format."}, 400

		query = UnivAuthorDB.query.filter(
			UnivAuthorDB.id == id).first()

		if not query:
			return {"message" : "No author Found."}, 404

		try:
			query.author = author
			query.author_normal = author_normal
			db.session.commit()
			return {'message' : 'Author data successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500

	# to change author's status from 'active' , 'banned' , 'on_hold'
	@jwt_required()
	@system_admin_required
	def put(self, id):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		status = data.get("status", None)
		status_norm = status.strip().lower()

		accepted = ['active' , 'banned' , 'on_hold']

		if not status or status is None:
			return {"message" : "No status data provided."}, 400

		if status_norm not in accepted:
			return {"message" : "Invalid Status."
			"status_example" : "Any from 'active' , 'banned' or 'on_hold'"}, 400

		query = UnivAuthorDB.query.filter(
			UnivAuthorDB.id == id).first()

		try:
			query.status = status_norm
			db.session.commit()
			return {'message' : 'Author status successfully updated.'}, 200
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : 'An error occured'}, 500

class AuthorCR(Resource):
	@jwt_required()
	@admin_required
	def get():
		pass
