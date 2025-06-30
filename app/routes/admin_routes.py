from flask import Blueprint
from flask_restful import Api
from app.resources.admin import Admin_Crud, Admin_Book_Manage, User_Control

admin_bp = Blueprint('admin', __name__, url_prefix='/a/v1')
admin_api = Api(admin_bp)

admin_api.add_resource(Admin_Crud, '/manage')
admin_api.add_resource(Admin_Book_Manage, '/books')
admin_api.add_resource(User_Control, '/user/ban')
