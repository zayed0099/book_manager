# dashboard.py
from flask import jsonify
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
	@limiter.limit("100 per day")
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

		books = []
		
		for data in choices:
			# Google Books API
			url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{data}&maxResults=20"
			response = request.get(GBAPIurl)

			if response.status_code == 200:
				data = response.json()

				for item in data['items']:
					books.append(item)
			else:
				return {'message' : 'An error occured'}, 500

		if len(books) < 5:
			return {'message' : 'An error occured.'}, 500

		random_books = random.sample(books, 5)

		data_to_send = []

		for book in random_books:
			data = {
			"title" : book["volumeInfo"]['title'],
			"author" : book["volumeInfo"]['authors'],
			"categories" : book["volumeInfo"]["categories"],
			"imageLinks" : book["volumeInfo"]["imageLinks"]
			}
			data_to_send.append(data)

		if len(data_to_send) < 5:
			return {'message' : 'An error occured.'}, 500

		return {'message' : f'These 5 books are recommended for user_id: {user_id}',
				'books' : jsonify(data_to_send),
				'most_read_genre' : genres
		}, 200


		