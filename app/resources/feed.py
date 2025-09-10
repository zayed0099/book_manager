# dashboard.py
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter
from app.services import (
	cache_get,
	cache_set
)

class BookDetails(Resource):
	@jwt_required()
	def get(self, id=None):
		from app.models import Ratings_Reviews
		from app.models.universaldata import (
				UnivBookDB,
				UnivAuthorDB,
				UnivPubDB,
				UnivCatDB,
				BookAuthorLink,
				BookPublLink,
				BookCatLink
			)

		filters = [
			UnivBookDB.status == "active",
			UnivAuthorDB.status == "active",
			UnivCatDB.status == "active",
			UnivPubDB.status == "active"
		]

		if id is not None:
			data = cache_get("feed:books")
			if data:
				for key, value in data.items():
					if key == id:
						return {
							"Status" : "Cache hit",
							"book" : value
						}, 200

			filters.extend([
				UnivBookDB.id == id,
				BookCatLink.book_id == id,
				BookPublLink.book_id == id,
				BookAuthorLink.book_id == id
			])

			all_query = (
				db.session.query(
					UnivBookDB.label("book"),
					func.group_concat(UnivAuthorDB.author).label('authors'),
					func.group_concat(UnivCatDB.category).label('categories'),
					UnivPubDB.publisher.label("publisher")
					)
				.join(UnivCatDB, BookCatLink.category_id == UnivCatDB.id)
				.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
				.join(UnivPubDB, BookPublLink.publisher_id == UnivPubDB.id)
				.filter(*filters)
				.first()
			)

			if not all_query:
				return {"error": "Book not found"}, 404

			book_details = {
				"title" : all_query.book.title,
				"subtitle" : all_query.book.subtitle,
				"description" : all_query.book.description,
				"isbn1" : all_query.book.isbn1,
				"isbn2" : all_query.book.isbn2,
				"imagelink" : all_query.book.imagelink,
				"pub_date" : all_query.book.pub_date,
				"page_count" : all_query.book.page_count,
				"language" : all_query.book.language,
			}

			author_details = all_query.authors.split(',')
			category = all_query.categories.split(",")
			publisher = []
			publisher.append(all_query.publisher)

			book_data = {
				"book" : book_details,
				"author" : author_details,
				"publisher" : publisher,
				"category" : category
			}

			return {
				"status" : "Cache Miss",
				"items" : book_data
			}, 200

		if not id:
			data = cache_get("feed:books")
			if data:
				return {
					"status" : "Cache hit",
					"books" : data				}

			subq = (
				db.session.query(
					Ratings_Reviews.book_id, 
					func.count().label("review_count"))
				.group_by(Ratings_Reviews.book_id)
				.order_by(desc("review_count"), Ratings_Reviews.book_id)
				.limit(5)
				.subquery()
			)

			results = (
				db.session.query(
					UnivBookDB.label("book"),
					func.group_concat(UnivAuthorDB.author).label('authors'),
					func.group_concat(UnivCatDB.category).label('categories'),
					UnivPubDB.publisher.label("publisher")
					)
				.join(UnivBookDB, UnivBookDB.id == subq.c.book_id)
				.join(UnivCatDB, BookCatLink.category_id == UnivCatDB.id)
				.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
				.join(UnivPubDB, BookPublLink.publisher_id == UnivPubDB.id)
				.filter(*filters)		
				.all()
			)

			if not results:
				return {"message" : "No book found."}, 404

			books = {}

			for detail in results:
				book_details = {
					"title" : results.book.title,
					"subtitle" : results.book.subtitle,
					"description" : results.book.description,
					"isbn1" : results.book.isbn1,
					"isbn2" : results.book.isbn2,
					"imagelink" : results.book.imagelink,
					"pub_date" : results.book.pub_date,
					"page_count" : results.book.page_count,
					"language" : results.book.language,
				}
				author_details = results.authors.split(',')
				category = results.categories.split(",")
				
				books[results.book.id] = {
						"book" : book_details,
						"authors" : author_details,
						"category" : category,
						"publisher" : results.publisher
					}

			cache_set(f"feed:books", books, ttl=300)

			return {
				"status" : "Successful",
				"books" : books
			}, 200
