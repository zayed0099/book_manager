from flask import Blueprint
from flask_restful import Api

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/v1')
auth_api = Api(auth_bp)

from app.resources.auth import AddUser, Login, Ref_Token, Del_Token, CheckUser, DeleteUser

# For new user regestration.
auth_api.add_resource(AddUser, '/register')

# For esisting user login.
auth_api.add_resource(Login, '/login')

# For refresh token works
auth_api.add_resource(Ref_Token, '/refresh')

'''for user logout. If a user sends a req in here 
the jwt token gets blacklisted'''
auth_api.add_resource(Del_Token, '/logout')

# User account deletion request/revoke by user himself
auth_api.add_resource(DeleteUser, '/user/delete')

'''To check if a user is valid or not!
If a user is valid, he will be able to access this road.'''
auth_api.add_resource(CheckUser, '/user/check')
