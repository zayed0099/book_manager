# dashboard.py
from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case, func
from datetime import datetime

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
		.group_by(book_manager.genre_normal)
		.order_by(desc("genre_count"))
		.all()
	)

	top_two = results[:2]

	if len(results) > 2:
		third_one = results[2][0]
		