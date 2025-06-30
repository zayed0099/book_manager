from flask_restful import Resource, request, abort
from app.extensions import limiter, db, jwt, user_schema, admin_required
from datetime import datetime, timezone
from app.models import User, book_manager, jwt_blacklist
from werkzeug.security import generate_password_hash
from app.errors.handlers import CustomBadRequest
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError

'''
admin can see how manu users in there. 
add new admin.
look how many books there are. who has how many books.
ban/mute a user
control flow of all new user joining/account deletion
'''

# A route to get all the admin info and ban/unban them
class admin_crud(Resource):
	@jwt_required()
	@admin_required()
	def get(self):
		page = request.args.get('page', 1, type=int)
		per_page = request.args.get('per_page', 5, type=int)

		pagination = User.query.filter(User.role == 'admin'
			,User.is_banned == False).paginate(
			page=page, per_page=per_page, error_out=False)

		if not pagination.items:
			abort(404, description="No admins found.")

		else:
			admins =  user_schema.dump(pagination.items, many=True)

			return {
			'admins': admins,
			'page': pagination.page,
			'per_page': pagination.per_page,
			'total_items': pagination.total,
			'total_pages': pagination.pages
			}, 200
	
	@jwt_required()
	@admin_required()
	def post(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		username_new_admin = data.get("username")
		pass_new_admin = data.get("password")
		now = datetime.now(timezone.utc)

		if not username_new_admin or not pass_new_admin:
			raise CustomBadRequest("Username and password required.")

		else:
			check_user = User.query.filter(User.username == username_new_admin).first()

			if check_user:
				return {'message' : 'User already exists. Change his role to admin with a put req.'}
			else:
				new_hashed_pw_admin = generate_password_hash(pass_new_admin)

				new_admin = User(username=username_new_admin
					,password=new_hashed_pw_admin
					,joined=now
					,role='admin')

				try:
					db.session.add(new_admin)
					db.session.commit()
					return {"Successful": "Head to '/login' to login and start using the api."}, 200
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e

	@jwt_required()
	@admin_required()
	def put(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		username_of_user = data.get("username")

		if not username_of_user:
			raise CustomBadRequest("Username required.")

		else:
			check_user = User.query.filter(User.username == username_of_user).first()

			if not check_user:
				abort(404, description="User not found in the database.")

			else:
				try:
					check_user.role = 'admin'
					db.session.commit()
					return {'message' : 'User added as admin successfully'}
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e


	@jwt_required()
	@admin_required()
	def delete(self):
		try:
			data = request.get_json()
			if data is None:
				raise CustomBadRequest("Missing JSON in request.")
		except BadRequest:
			raise CustomBadRequest("Invalid JSON format.")

		username_of_user = data.get("username")

		if not username_of_user:
			raise CustomBadRequest("Username required.")

		else:
			check_user = User.query.filter(User.username == username_of_user
				,User.role == 'admin').first()

			if not check_user:
				return {'message' : 'user is not an admin.'}

			else:
				try:
					check_user.role = 'user'
					db.session.commit()
					return {'message' : 'User removed from admin. Go to /user/manage to ban him from being a user too.'}
				except SQLAlchemyError as e:
					db.session.rollback()
					raise e