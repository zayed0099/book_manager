# dashboard.py
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case, func
from datetime import datetime
import requests
import random

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import limiter

'''
plan for this section:
- recommend users books based on the genres theyve readed the most (main bookd db + book_manager)
- count of all books they've read total + etc etc(book_manager)
- streak counter system of a book they're reading currently
'''
class StatBooks(Resource):
	@jwt_required()
	@limiter.limit("100 per day")
	def get(self):
		from app.models import book_manager
		user_id = get_jwt_identity()

		result = db.session.query(
			func.count(book_manager.id),
			func.sum(case([(book_manager.favourite == True, 1)], else_=0)),
			func.sum(case([(book_manager.is_deleted == True, 1)], else_=0))
			).filter(book_manager.user_id == user_id).one()

		if result[0] == 0:
			return {'message' : 'No data for that specific user'}, 200

		total_books = result[0]
		total_favourites = result[1]
		total_deleted = result[2]
		
		return {
			'total_book' : total_books,
			'total_fav' : total_favourites,
			'total_del' : total_deleted,
		}, 200

class RecoBook(Resource):
	@jwt_required()
	def get(self):
		from app.models import book_manager
		user_id = get_jwt_identity()

		results = (
			db.session.query(
				book_manager.genre_normal,
				func.count().label("genre_count")
			)
			.filter(book_manager.user_id == user_id)
			.group_by(book_manager.genre_normal)
			.order_by(desc("genre_count"), book_manager.genre_normal)
			.limit(5)
			.all()
		)

		genres = [genre for genre, count in results]

		if len(genres) < 2:
			return {'message' : 'Not enough genre for Book recommendation.'}, 403

		choices = []
		choices = random.sample(genres, 2) # to get 2 diff genre from the list genres

		if len(choices) < 2:
			return {'message' : 'Not enough genre for Book recommendation.'}, 403
		
		# Google Books API
		url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{choices[0]}+subject:{choices[1]}&maxResults=5"
		response = requests.get(url)

		books = []
		
		if response.status_code == 200:
			data = response.json()

			for item in data.get('items', []):
				book = item.get("volumeInfo", {})
				
				single_book_data = {
				"title" : book.get("title", None),
				"authors" : book.get("authors", None),
				"description" : book.get("description", None),
				"imageLinks" : book.get("imageLinks", None)
				}
				books.append(single_book_data)
		else:
			return {'message' : 'An error occured'}, 500

		if len(books) == 0:
			return {'message' : 'No book could be recommended.'}, 500


		return {'message' : f'These books are recommended for user_id: {user_id}',
				'books' : books,
				'most_read_genre' : genres
		}, 200

class RatingOwn(Resource):
	@jwt_required()
	@limiter.limit("100 per day")
	def get(self, id):
		pass