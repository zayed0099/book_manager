# db_inserts.py
from flask_restful import Resource, request, abort
from datetime import datetime, timezone, timedelta
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError

# Local Import
from app.extensions import db
from app.errors.handlers import CustomBadRequest
from app.jwt_extensions import (jwt, 
	limiter,
	admin_required,
	system_admin_required)
from app.models import (UnivBookDB, 
			UnivAuthorDB,
			UnivPubDB, 
			BookAuthorLink,
			BookPublLink) 

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

		title = data.get("title", None)
		if title is None:
			return {'message' : "Book w/o title can't be accepted"}, 400
		normalized_title = title.strip().lower()

		subtitle = data.get("subtitle", None)

		# Category Section
		category1 = data.get("category1", None)
		if category1 is not None:
			category1_normal = category1.strip().lower()

		category2 = data.get("category2", None)
		if category2 is not None:
			category2_normal = category2.strip().lower()

		description = data.get("description", None)

		if description is not None:
			words = description.split()
			check = len(words)
			if check > 250:
				return {'message' : 'The description is too long.'}, 400

		isbn1 = data.get("isbn1", None)
		isbn2 = data.get("isbn2", None)

		imagelink = data.get("imagelink")
		if imagelink is None:
			return {'message' : "Data w/o [imagelink] can't be accepted."}, 400

		pub_date = data.get("pub_date", None)
		page_count = data.get("page_count", None)
		language = data.get("language", "en")

		# Author Section
		author1 = data.get("author1", None)
		
		if author1 is None:
			return {'message' : "A book w/o author can't be accepted."}, 400
		
		author1_normal = author1.strip().lower()

		author2 = data.get("author2", None)
		if author2 is not None:
			author2_normal = author2.strip().lower()

		author3 = data.get("author3", None)
		if author3 is not None:
			author3_normal = author3.strip().lower()

		author4 = data.get("author4", None)
		if author4 is not None:
			author4_normal = author4.strip().lower()

		author5 = data.get("author5", None)
		if author5 is not None:
			author5_normal = author5.strip().lower()
			
		try:
			author1_check = UnivAuthorDB.query.filter_by(
				author_normal=author1_normal).first()

			if author1_check is None:
				author1_new = UnivAuthorDB(
					author = author1,
					author_normal = author1_normal)
				db.session.add(author1_new)

			if author2 is not None:
				author2_check = UnivAuthorDB.query.filter_by(
				author_normal=author2_normal).first()

				if author2_check is None:
					author2_new = UnivAuthorDB(
						author = author2,
						author_normal = author2_normal)
					db.session.add(author2_new)
			
			if author3 is not None:
				author3_check = UnivAuthorDB.query.filter_by(
				author_normal=author3_normal).first()

				if author3_check is None:
					author3_new = UnivAuthorDB(
						author = author3,
						author_normal = author3_normal)
					db.session.add(author3_new)

			if author4 is not None:
				author4_check = UnivAuthorDB.query.filter_by(
				author_normal=author4_normal).first()

				if author4_check is None:
					author4_new = UnivAuthorDB(
						author = author4,
						author_normal = author4_normal)
					db.session.add(author4_new)

			if author5 is not None:
				author5_check = UnivAuthorDB.query.filter_by(
				author_normal=author5_normal).first()

				if author5_check is None:
					author5_new = UnivAuthorDB(
						author = author5,
						author_normal = author5_normal)
					db.session.add(author5_new)

			new_book = UnivBookDB(
				title = title,
				normalized_title = normalized_title,
				subtitle = subtitle,
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

			if isbn1 or isbn2:
				isbn_filters = []

				if isbn1 is not None:
					isbn_filters.append(UnivBookDB.isbn1 == isbn1)
				if isbn2  is not None:
					isbn_filters.append(UnivBookDB.isbn2 == isbn2)

				query = db.session.query(UnivBookDB).filter(or_(*filters)).first()				

			else:
				filters = []
				filters.append(UnivBookDB.normalized_title == normalized_title)
				filters.append(UnivAuthorDB.author_normal == author1_normal)

				query =( 
					db.session.query(UnivBookDB)
					.join(BookAuthorLink, BookAuthorLink.book_id == UnivBookDB.id)
					.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
					.filter(*filters)
					.first()
				)

			if query is None:
				db.session.add(new_book)
				db.session.flush()
			else:
				return {'message' : 'Book already exists.'}, 409

			book_id = new_book.id

			author_ids = []
			author1_id = author1_new.id if author1_check is None else author1_check.id
			author_ids.append(author1_id)

			author2_id = None
			author3_id = None
			author4_id = None
			author5_id = None

			if author2 is not None:
				author2_id = author2_new.id if author2_check is None else author2_check.id
				author_ids.append(author2_id)

			if author3 is not None:
				author3_id = author3_new.id if author3_check is None else author3_check.id
				author_ids.append(author3_id)

			if author4 is not None:
				author4_id = author4_new.id if author4_check is None else author4_check.id
				author_ids.append(author4_id)

			if author5 is not None:
				author5_id = author5_new.id if author5_check is None else author5_check.id
				author_ids.append(author5_id)

			for author_id in author_ids:
				book_author_link_entry = BookAuthorLink(
					book_id = book_id,
					author_id = author_id
					)
				db.session.add(book_author_link_entry)
			
			publisher = data.get("publisher", None)

			if publisher is None:
				none_pub_entry = UnivPubDB(
					publisher="unknown",
					publisher_normal="unknown")
				db.session.add(none_pub_entry)
				db.session.flush()

				none_pub_link = BookPublLink(
					book_id=book_id,
					publisher_id=none_pub_entry.id)
				db.session.add(none_pub_link)

			else:
				publisher_normal = publisher.strip().lower()
				pub_query = UnivPubDB.query.filter_by(
					publisher_normal=publisher_normal).first()

				if pub_query is None:
					new_pub = UnivPubDB(
						publisher=publisher,
						publisher_normal=publisher_normal)
					db.session.add(new_pub)
					db.session.flush()

					new_publink_entry_1 = BookPublLink(
						book_id=book_id,
						publisher_id=new_pub.id)
					db.session.add(new_publink_entry_1)
				
				else:
					new_publink_entry_2 = BookPublLink(
						book_id=book_id,
						publisher_id=pub_query.id)
					db.session.add(new_publink_entry_2)

			db.session.commit()
			return {'message' : 'Book successfully added'}, 201
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : str(e)}, 500
