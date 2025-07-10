from flask import Blueprint
from flask_restful import Api

book_bp = Blueprint('book', __name__)
book_api = Api(book_bp)

from app.resources.book import Book_CR, Book_RUD, Book_reuse, Book_Favourite_get, Book_Favourite_ud

book_api.add_resource(Book_CR, '/api/v1/books', endpoint='view')  # For Create & Read (all)
book_api.add_resource(Book_RUD, '/api/v1/books/<int:id>', endpoint='edit_delete')  # For Read (one), Update, Delete

book_api.add_resource(Book_reuse, '/api/v1/recovery', endpoint='recover')

# One to get all favourites and another to update and delete them.
book_api.add_resource(Book_Favourite_get, '/api/v1/favourites', endpoint='favourite')
book_api.add_resource(Book_Favourite_ud, '/api/v1/favourites/<int:id>', endpoint='favourite_ud')