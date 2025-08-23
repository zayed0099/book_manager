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

		publisher_raw = data.get("publisher", None)
		if isinstance(publisher_raw, str):
			publisher = publisher_raw
			publisher_normal = publisher.strip().lower()
		else:
			publisher = None

		categories = data.get("categories", None)
		if categories is not None and isinstance(categories, list):
			category_filtered = []
			for category in categories:
				if isinstance(category, str) and category.lower().strip() != 'uncategorized':
					category_filtered.append(category)
			if len(category_filtered) == 0:
				category_filtered = None
		else:
			category_filtered = None

		try:
			book_duplicate_filters = []
			
			for author_ in authors:
				author_norm =  author_.lower().strip()
				book_duplicate_filters.append(
					UnivAuthorDB.author_normal == author_norm)

			book_duplicate_check =( 
				db.session.query(UnivBookDB.id)
				.join(BookAuthorLink, BookAuthorLink.book_id == UnivBookDB.id)
				.join(UnivAuthorDB, BookAuthorLink.author_id == UnivAuthorDB.id)
				.filter(
					UnivBookDB.normalized_title == normalized_title,
					or_(*book_duplicate_filters)
				)
				.first()
			)

			book_exists = bool(book_duplicate_check)

			if book_exists:
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
				'matched title' : query.normalized_title
				}
				return {'message' : 'Book already exists.',
				'debug' : debug_dict}, 409

			book_id = new_book.id

			# Query to check author, category and publisher status
			duplicate_check =( 
				db.session.query(
					UnivAuthorDB.id.label("author_id"),
					UnivAuthorDB.author_normal.label("author"),
					UnivCatDB.id.label("category_id"),
					UnivCatDB.category_normal.label("category"),
					UnivPubDB.id.label("publisher_id"),
					UnivPubDB.publisher_normal.label("publisher")
				)
				.outerjoin(UnivCatDB)
				.outerjoin(UnivPubDB)
				.all()
			)

			authors_set = set()
			categories_set = set()
			publishers_set = set()

			for row in duplicate_check:
				if row.author_id:
					authors_set.add((row.author_id, row.author))
				if row.category_id:
					categories_set.add((row.category_id, row.category))
				if row.publisher_id:
					publishers_set.add((row.publisher_id, row.publisher))

			# list of tuples 
			authors_list = list(authors_set)
			categories_list = list(categories_set)
			publishers_list = list(publishers_set)

			author_dict = {}
			category_dict = {}
			publisher_dict = {}

			for author_id, author_name in authors_list:
				author_dict[author_name] = {'id' : author_id}

			for category_id, category_name in categories_list:
				category_dict[category_name] = {'id' : category_id}

			for publisher_id, publisher_name in publishers_list:
				publishers_list[publisher_name] = {'id' : publisher_id}
				
			for author in authors:
				author_norm =  author.lower().strip()
				if author_norm in author_dict:
					author_id = auth_dict[author_norm]["id"]
					new_auth_book_link = BookAuthorLink(
						book_id=book_id, author_id=author_id)
					db.session.add(new_auth_book_link)
			
				else:
					new_author = UnivAuthorDB(
						author=author, author_normal=author_norm)
					db.session.add(new_author)
					db.session.flush()

					new_auth_book_link = BookAuthorLink(
						book_id=book_id, author_id=new_author.id)
					db.session.add(new_auth_book_link)
				
				
			if publisher is None:
				if "unknown" in publisher_dict:
					publisher_id = publisher_dict["unknown"]["id"]
					none_pub_link = BookPublLink(
						book_id=book_id, publisher_id=publisher_id)
					db.session.add(none_pub_link)
				else:
					none_pub_entry = UnivPubDB(
						publisher="unknown", publisher_normal="unknown")
					db.session.add(none_pub_entry)
					db.session.flush()

					none_pub_link = BookPublLink(
						book_id=book_id, publisher_id=none_pub_entry.id)
					db.session.add(none_pub_link)

			else:
				if publisher_normal in publisher_dict:
					publisher_id = publisher_dict[publisher_normal]["id"]
					new_publink_entry_2 = BookPublLink(
						book_id=book_id, publisher_id=publisher_id)
					db.session.add(new_publink_entry_2)

				else:
					new_pub = UnivPubDB(
						publisher=publisher, publisher_normal=api_publisher_norm)
					db.session.add(new_pub)
					db.session.flush()

					new_publink_entry_1 = BookPublLink(
						book_id=book_id, publisher_id=new_pub.id)
					db.session.add(new_publink_entry_1)
					

			# Category Section			
			if category_filtered is None:
				if 'uncategorized' in category_dict:
					category_id = category_dict['uncategorized']['id']
					uncat_link_entry_1 = BookCatLink(
						book_id=book_id, category_id=category_id)
					db.session.add(uncat_link_entry_1)
				
				else:
					uncategorized_entry = UnivCatDB(
						category = 'uncategorized' , category_normal= 'uncategorized')
					db.session.add(uncategorized_entry)
					db.session.flush()

					uncat_link_entry_2 = BookCatLink(
						book_id=book_id, category_id=uncategorized_entry.id)
					db.session.add(uncat_link_entry_2)

			else:
				for filtered_category in category_filtered:
					api_category_normal = filtered_category.lower().strip()
					
					if api_category_normal in category_dict:
						category_id = category_dict[api_category_normal]['id']
						new_book_cat_link = BookCatLink(
							book_id = book_id, category_id = category_id)
						db.session.add(new_book_cat_link)

					else:
						new_category = UnivCatDB(
							category=filtered_category, 
							category_normal=api_category_normal)
						db.session.add(new_category)
						db.session.flush()
						
						new_book_cat_link = BookCatLink(
							book_id = book_id,
							category_id = new_category.id)
						db.session.add(new_book_cat_link)

			db.session.commit()
			return {'message' : 'Book successfully added'}, 201
		except SQLAlchemyError as e:
			db.session.rollback()
			return {'message' : str(e)}, 500



			'''
			# The duplicate checking query i did previously
			filters = []
			
			for author_ in authors:
				author_norm =  author_.lower().strip()
				filters.append(or_(
					UnivAuthorDB.author_normal == author_norm,
					UnivAuthorDB.author_normal.is_(None)))

			if publisher is None:
				filters.append(or_(
					UnivPubDB.publisher_normal == "unknown",
					UnivPubDB.publisher_normal.is_(None)
				))
			else:
				filters.append(UnivPubDB.publisher_normal == publisher.lower().strip())

			if len(category_filtered) == 0:
				filters.append(UnivCatDB.category_normal == 'uncategorized')
			else:
				for category_ in category_filtered:
					filters.append(or_(
						UnivCatDB.category_normal == category_.lower().strip(),
						UnivCatDB.category_normal.is_(None)
					))
			'''