# dashboard.py
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter


class BookDetails(Resource):
	@jwt_required()
	def get(self, id):
		from app.models.universaldata import (
			UnivBookDB,
			UnivAuthorDB,
			UnivPubDB,
			UnivCatDB,
			BookAuthorLink,
			BookPublLink,
			BookCatLink)

		filters = [
			UnivBookDB.id == id,
			UnivBookDB.status == "active",
			UnivAuthorDB.status == "active",
			UnivCatDB.status == "active",
			UnivPubDB.status == "active",
			BookCatLink.book_id == id,
			BookPublLink.book_id == id,
			BookAuthorLink.book_id == id,
		]

		all_query = (
			db.session.query(
				UnivBookDB.label("book"),
				UnivAuthorDB.author.label("author"),
				UnivCatDB.category.label("category"),
				UnivPubDB.publisher.label("publisher"))
			.join(UnivCatDB, BookCatLink.category_id == UnivCatDB.id)
			.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
			.join(UnivPubDB, BookPublLink.publisher_id == UnivPubDB.id)
			.filter(*filters)
			.all()
		)

		if not all_query:
			return {"error": "Book not found"}, 404

		author_details = set()
		publisher = []
		category = set()
		
		is_book_data_fetched = False
		is_publisher_data_fetched = False


		for data in all_query:
			if not is_book_data_fetched:
				book_details = {
					"title" : data.book.title,
					"subtitle" : data.book.subtitle,
					"description" : data.book.description,
					"isbn1" : data.book.isbn1,
					"isbn2" : data.book.isbn2,
					"imagelink" : data.book.imagelink,
					"pub_date" : data.book.pub_date,
					"page_count" : data.book.page_count,
					"language" : data.book.language,
				}
				is_book_data_fetched = True
			
			author_details.add(data.author)
			category.add(data.category)
			
			if not is_publisher_data_fetched:
				publisher.append(data.publisher)
				is_publisher_data_fetched = True

		return {
			"status" : "Successful",
			"book_details" : book_details,
			"authors" : list(author_details),
			"publisher" : publisher,
			"category" : list(category)
		}, 200




