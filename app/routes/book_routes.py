from flask import Blueprint
from flask_restful import Api

book_bp = Blueprint('book', __name__)
book_api = Api(book_bp)

from app.resources.book import Book_CR, Book_RUD, Book_reuse, Book_Favourite
book_api.add_resource(Book_CR, '/api/v1/books', endpoint='view')  # For Create & Read (all)
book_api.add_resource(Book_RUD, '/api/v1/books/<int:id>', endpoint='edit_delete')  # For Read (one), Update, Delete
book_api.add_resource(Book_reuse, '/api/v1/recovery', endpoint='recover')
book_api.add_resource(Book_reuse, '/api/v1/favourites', endpoint='favourite')