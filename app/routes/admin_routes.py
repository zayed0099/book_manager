from flask import Blueprint
from flask_restful import Api

admin_bp = Blueprint('admin', __name__, url_prefix='/a/v1')
admin_api = Api(admin_bp)

from app.resources.admin import (Admin_Crud, 
	Admin_Book_Manage, 
	User_Control, 
	Jwt_Manage, 
	UserCredChange,
	AdminUD,
	User_Show,
	BookManage,
	UserAccDelete)

# Admin seeing all admin data, Adding completely new user as admin
admin_api.add_resource(Admin_Crud, '/manage')

# Adding/Removing existing user from admin.
admin_api.add_resource(AdminUD, '/manage/<int:id>')

# Admin wanting to see all the books in the db regardless of user
admin_api.add_resource(Admin_Book_Manage, '/books')

# Banning/Unbanning a user from the api.
admin_api.add_resource(User_Control, '/user/ban/<int:id>')

# Getting all user data
admin_api.add_resource(User_Show, '/user/view')

# Reseting user password
admin_api.add_resource(UserCredChange, '/user/reset')

# Clearing JWT tokens
admin_api.add_resource(Jwt_Manage, '/jwt/clear')

# Clearing all soft deleted books from book database
admin_api.add_resource(BookManage, '/book/clear')

# Clearing all user with delete acc req, 
# older than 30 days from User database
admin_api.add_resource(UserAccDelete, '/user/clear')


