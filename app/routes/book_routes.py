from flask import Blueprint
from flask_restful import Api

book_bp = Blueprint('book', __name__, url_prefix='/api/v1')
book_api = Api(book_bp)

from app.resources.book import (
    Book_CR,
    Book_RUD,
    Book_reuse,
    Book_Favourite_get,
    Book_Favourite_ud,
    BookRecover
)

from app.resources.book_manage import (
	BookRatings,
	BookRatings_UD,
	Tags
)

from app.resources.book_list import (
    BookListName,
    CustomBookList
)

# To add new Books + update/delete
book_api.add_resource(Book_CR, '/books', endpoint='view')  # For Create & Read (all)
book_api.add_resource(Book_RUD, '/books/<int:id>', endpoint='edit_delete')  # For Read (one), Update, Delete

# first one to see all deleted books, second to recover them
book_api.add_resource(Book_reuse, '/recovery', endpoint='recover')
book_api.add_resource(BookRecover, '/recovery/<int:id>', endpoint='recdeleted')

# One to get all favourites and another to update and delete them.
book_api.add_resource(Book_Favourite_get, '/favourites', endpoint='favourite')
book_api.add_resource(Book_Favourite_ud, '/favourites/<int:id>', endpoint='favourite_ud')

# To get id specific or all reviews
book_api.add_resource(BookRatings, '/reviews', endpoint='review')
book_api.add_resource(BookRatings, '/reviews/<int:id>', endpoint='review_one')

# To edit and delete review/rating => (PATCH, DELETE)
book_api.add_resource(BookRatings_UD, '/reviews/edit/<int:id>', endpoint='review_edit_del')

# Tagging 
book_api.add_resource(Tags, '/tags', endpoint='tagging_for_search')

# Custom Book List
book_api.add_resource(BookListName, '/booklist', endpoint='blist_naming')
book_api.add_resource(CustomBookList, '/booklist/add', endpoint='blist_adding')
book_api.add_resource(CustomBookList, '/booklist/add/<int:id>', endpoint='blist_PATCH_DEL')
