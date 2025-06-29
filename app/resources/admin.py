from flask_restful import Resource, request, abort
from app.extensions import limiter, db, jwt, user_schema, admin_required
from datetime import datetime

class admin_info(Resource):
    @jwt_required()
    def get(self):
    	pass