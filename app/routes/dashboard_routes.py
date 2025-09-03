from flask import Blueprint
from flask_restful import Api

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')
dashboard_api = Api(dashboard_bp)

from app.resources.dashboard import (
    StatBooks,
    RecoBook
)

from app.resources.feed import BookDetails

# To get stat of total book, fav book, deleted book
dashboard_api.add_resource(StatBooks, '/stat', endpoint='stat')

# To recommend books to a user based on his most read genre
dashboard_api.add_resource(RecoBook, '/recommend', endpoint='recommend')

# News Feed Route to show book to a user 
dashboard_api.add_resource(BookDetails, '/bookdetails', endpoint='bookdetails')