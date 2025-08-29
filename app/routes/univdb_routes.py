# All routes here are Admin Only Routes
from flask import Blueprint
from flask_restful import Api

from app.resources import (
	AddBook,
	AuthorCRUD,
	PublisherUD)

univdb_bp = Blueprint('univdb', __name__, url_prefix='/univdb/v1')
univdb_api = Api(univdb_bp)

# Adding bulk books in Universal Book DB
univdb_api.add_resource(AddBook, '/add')

# ================Author Section

# Get all authors and Adding Author one by one
univdb_api.add_resource(AuthorCRUD, '/author')

# Author Patch/Delete
univdb_api.add_resource(AuthorCRUD, '/author/<int:id>')

# ================Publisher Section

# Get all publisher and Adding publisher one by one
# univdb_api.add_resource(AuthorCRUD, '/author')

# Publisher Patch/Delete
univdb_api.add_resource(PublisherUD, '/pub/<int:id>')
