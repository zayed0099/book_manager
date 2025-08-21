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
			UnivCatDB,
			BookAuthorLink,
			BookPublLink,
			BookCatLink) 

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

		description = data.get("description", None)

		if description is not None:
			words = description.split()
			check = len(words)
			if check > 250:
				return {'message' : 'The description is too long.'}, 400

		isbn1_raw = data.get("isbn1", None)
		isbn2_raw = data.get("isbn2", None)

		if isbn1_raw is not None:
			isbn1 = isbn1_raw.upper().replace("ISBN:", "").replace("ISBN", "").replace("-", "").replace(" ", "")
		if isbn2_raw is not None:
			isbn2 = isbn1_raw.upper().replace("ISBN:", "").replace("ISBN", "").replace("-", "").replace(" ", "")

		imagelink = data.get("imagelink", None)
		if imagelink is None:
			return {'message' : "Data w/o [imagelink] can't be accepted."}, 400

		pub_date = data.get("pub_date", None)
		page_count = data.get("page_count", None)
		language = data.get("language", "unknown")
		
		authors = data.get("authors", None)

		if authors is None or not isinstance(authors, list) or len(authors) == 0:
			return {'message' : "The book can't be accepted"}, 400
		
		for auth in authors:
			if not isinstance(auth, str):
				return {'message' : "The book can't be accepted"}, 400

		try:
			new_book = UnivBookDB(
				title = title,
				normalized_title = normalized_title,
				subtitle = subtitle,
				description = description,
				isbn1 = isbn1 if isbn1_raw is not None else None,
				isbn2 = isbn2 if isbn2_raw is not None else None,
				imagelink = imagelink,
				pub_date = pub_date,
				page_count = page_count,
				language = language
				)
			
			filters = []
			
			for author_ in authors:
				author_norm =  author_.lower().strip()
				filters.append(UnivAuthorDB.author_normal == author_norm)

			query =( 
				db.session.query(UnivBookDB)
				.join(BookAuthorLink, BookAuthorLink.book_id == UnivBookDB.id)
				.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
				.filter(
					UnivBookDB.normalized_title == normalized_title,
					or_(*filters)
				)
				.first()
			)

			if query is None:
				db.session.add(new_book)
				db.session.flush()
			else:
				debug_dict = {
				'title' : normalized_title,
				'matched title' : query.normalized_title
				}
				return {'message' : 'Book already exists.',
				'debug' : debug_dict}, 409

			book_id = new_book.id

			# Author Section
			for author in authors:
				author_normal = author.lower().strip()
				author_check = UnivAuthorDB.query.filter_by(
						author_normal=author_normal).first()

				if author_check is None:
					new_author = UnivAuthorDB(
						author=author,
						author_normal=author_normal)
					db.session.add(new_author)
					db.session.flush()

					new_auth_book_link = BookAuthorLink(
						book_id=book_id,
						author_id=new_author.id)
					db.session.add(new_auth_book_link)
				else:
					new_auth_book_link = BookAuthorLink(
						book_id=book_id,
						author_id=author_check.id)
					db.session.add(new_auth_book_link)

			publisher = data.get("publisher", None)

			if publisher is None:
				query = UnivPubDB.query.filter_by(
					publisher_normal='unknown').first()
				
				if query is None:
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
					none_pub_link = BookPublLink(
						book_id=book_id,
						publisher_id=query.id)
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

			# Category Section
			categories = data.get("categories", None)

			if categories is not None and isinstance(categories, list):
				category_filtered = []
				for category in categories:
					if isinstance(category, str) and category.lower().strip() != 'uncategorized':
						category_filtered.append(category)
				
				if len(category_filtered) == 0:
					category_filtered.append('uncategorized')
			else:
				category_filtered = ['uncategorized']
			
			for filtered_category in category_filtered:
				category_normal = filtered_category.lower().strip()
				category_check = UnivCatDB.query.filter_by(
					category_normal=category_normal).first()

				if category_check is None:
					new_cat_entry = UnivCatDB(
						category = filtered_category,
						category_normal = category_normal)
					db.session.add(new_cat_entry)
					db.session.flush()

					new_book_cat_link = BookCatLink(
						book_id = book_id,
						category_id = new_cat_entry.id)
					db.session.add(new_book_cat_link)
				else:
					new_book_cat_link = BookCatLink(
						book_id = book_id,
						category_id = category_check.id)
					db.session.add(new_book_cat_link)

			db.session.commit()
			return {'message' : 'Book successfully added'}, 201
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : str(e)}, 500
