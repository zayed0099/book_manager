from flask import Blueprint
from flask_restful import Api
from app.resources.auth import AddUser, Login, Ref_Token, Del_Token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/v1')
auth_api = Api(auth_bp)

auth_api.add_resource(AddUser, '/register')
auth_api.add_resource(Login, '/login')
auth_api.add_resource(Ref_Token, '/refresh')
auth_api.add_resource(Del_Token, '/logout')
