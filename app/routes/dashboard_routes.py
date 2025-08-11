from flask import Blueprint
from flask_restful import Api

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')
dashboard_api = Api(dashboard_bp)

from app.resources.dashboard import (
    StatBooks
)

# To get stat of total book, fav book, deleted book
dashboard_api.add_resource(StatBooks, '/stat', endpoint='stat')