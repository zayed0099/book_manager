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

	choices = []

	while len(choices) <= 1:
		# random choice a genre > add that to choices > remove that from genres to avoid duplicates
		choice = random.choice(genres)
		choices.append(choice)
		genres.remove(choice)

		if len(choices) == 2:
			break

	GBAPIurl = f"https://www.googleapis.com/books/v1/volumes?q=subject:{choices[0]}+subject:{choices[1]}&maxResults=20"

	if len(choices) == 0:
		return {'message' : 'An error occured.'}, 500

	response = request.get(GBAPIurl)

	if response.status_code == 200:
		data = response.json()

		books = []

		for item in data['items']:
			books.append(item)

		book_count = []

		while len(book_count) <= 4:
			selected = random.choice(books)
			book_count.append(selected)
			books.remove(selected)
			if len(book_count) == 5:
				break

		for book in book_count:
			

	else:
		return {'message' : 'An error occured'}, 500


		