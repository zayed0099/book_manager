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
from app.jwt_extensions import (
	jwt, 
	limiter,
	admin_required)
from app.models import (
	UnivBookDB, 
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
			return {'message' : "Book without 'title' can't be accepted"}, 400
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
			isbn2 = isbn2_raw.upper().replace("ISBN:", "").replace("ISBN", "").replace("-", "").replace(" ", "")

		imagelink = data.get("imagelink", None)
		if imagelink is None:
			return {'message' : "Data without 'imagelink' can't be accepted."}, 400

		pub_date = data.get("pub_date", None)
		page_count = data.get("page_count", None)
		language = data.get("language", "unknown")
		
		authors = data.get("authors", None)

		authors_norm = []
		author_norm_dict = {}

		if authors is None or len(authors) == 0:
			return {
			'message' : "Invalid authors field.",
			'reason' : "Authors list cannot be empty. Must be a list of strings.",
			'example_authors' : "['Donald E. Knuth' , 'Robert C. Martin']"}, 400
		
		if not isinstance(authors, list): 
			return {
			'message' : "Invalid authors field.",
			'reason' : 'Authors must be provided as a list of strings.',
			'example_authors' : "['Donald E. Knuth' , 'Robert C. Martin']"}, 400

		for auth in authors:
			if not isinstance(auth, str):
				return {
				'message' : "Invalid authors field.",
				'reason' : "All items in the authors list must be strings.",
				'example_authors' : "['Donald E. Knuth' , 'Robert C. Martin']"}, 400

			else:
				auth_norm = auth.strip().lower()
				authors_norm.append(auth_norm)
				author_norm_dict[auth_norm] = {'raw_auth' : auth} 

		try:
			book_duplicate_check =( 
				db.session.query(
					UnivBookDB.id.label("id"),
					UnivBookDB.normalized_title.label("normalized_title"))
				.join(BookAuthorLink, BookAuthorLink.book_id == UnivBookDB.id)
				.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
				.filter(
					UnivBookDB.normalized_title == normalized_title,
					UnivAuthorDB.author_normal.in_(authors_norm)
				)
				.first()
			)

			book_exists = bool(book_duplicate_check)

			if not book_exists:
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

				db.session.add(new_book)
				db.session.flush()
			
			else:
				debug_dict = {
				'title' : normalized_title,
				'matched title' : book_duplicate_check.normalized_title
				}
				return {'message' : 'Book already exists.',
				'debug' : debug_dict}, 409

			book_id = new_book.id
			
			# authors section
			author_query = UnivAuthorDB.query.filter(
				UnivAuthorDB.author_normal.in_(authors_norm)
			).all()

			authors_dict = {}
				
			for author in author_query:
				authors_dict[author.author_normal] = {"id" : author.id}

			missing_authors = [
			{"norm" : auth, "raw_auth" : author_norm_dict[auth]["raw_auth"]}
			for auth in author_norm_dict
			if auth not in authors_dict
			]
			 
			if len(authors_dict) > 0:
				for author_norm in authors_dict:
					author_id = authors_dict[author_norm]["id"]
					new_auth_book_link = BookAuthorLink(
						book_id=book_id, author_id=author_id)
					db.session.add(new_auth_book_link)

			if len(missing_authors) > 0:
				for author in missing_authors:
					new_author = UnivAuthorDB(
						author=author["raw_auth"], author_normal=author["norm"])
					db.session.add(new_author)
					db.session.flush()

					new_auth_book_link = BookAuthorLink(
						book_id=book_id, author_id=new_author.id)
					db.session.add(new_auth_book_link)
			
			# Publisher Section
			publisher_raw = data.get("publisher", None)

			if publisher_raw is not None and isinstance(publisher_raw, str):
				publisher = publisher_raw
				publisher_normal = publisher.strip().lower()
			else:
				publisher_normal = "unknown"
			
			publisher_check = UnivPubDB.query.filter(
					UnivPubDB.publisher_normal == publisher_normal).first()
			
			if publisher_check is None:
				unknown_pub_add = UnivPubDB(
					publisher="unknown", publisher_normal="unknown")
				db.session.add(unknown_pub_add)
				db.session.flush()

				unknown_pub_link = BookPublLink(
					book_id=book_id, publisher_id=unknown_pub_add.id)
				db.session.add(unknown_pub_link)
			
			else:
				if publisher_check:
					new_publink_entry_2 = BookPublLink(
						book_id=book_id, publisher_id=publisher_check.id)
					db.session.add(new_publink_entry_2)

				else:
					new_pub = UnivPubDB(
						publisher=publisher, publisher_normal=publisher_normal)
					db.session.add(new_pub)
					db.session.flush()

					new_publink_entry_1 = BookPublLink(
						book_id=book_id, publisher_id=new_pub.id)
					db.session.add(new_publink_entry_1)
					
			# Category Section
			categories = data.get("categories", None)
			
			category_normal = []
			category_normal_dict = {}
			
			if categories is not None and isinstance(categories, list):
				for category in categories:
					if isinstance(category, str):
						normal_category = category.lower().strip()
						if normal_category != 'uncategorized':
							category_normal.append(normal_category)
							category_normal_dict[normal_category] = {"raw_category" : category}

				if len(category_normal) == 0:
					category_normal.append('uncategorized')

			else:
				category_normal.append('uncategorized')

			category_check = UnivCatDB.query.filter(
				UnivCatDB.category_normal.in_(category_normal)).all()

			existing_category = {row.category_normal : {"id" : row.id} for row in category_check}

			missing_categories = [
			{"norm" : category , "raw_category" : category_normal_dict[category]["raw_category"]}
			for category in category_normal_dict
			if category not in existing_category
			]

			if len(existing_category) > 0:
				for catg in existing_category:
					category_id = catg['id']
					uncat_link_entry_1 = BookCatLink(
						book_id=book_id, category_id=category_id)
					db.session.add(uncat_link_entry_1)

			if len(missing_categories) > 0:
				for catg in missing_categories:
					new_catg = UnivCatDB(category=catg["raw_category"],
						category_normal=catg)

					db.session.add(new_catg)
					db.session.flush()

					new_link = BookCatLink(
						book_id=book_id, category_id=new_catg.id)
					db.session.add(new_catg)

			db.session.commit()
			return {'message' : 'Book successfully added'}, 201
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : str(e)}, 500
