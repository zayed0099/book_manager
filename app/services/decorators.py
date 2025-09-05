from flask import request
from flask_jwt_extended import get_jwt
from functools import wraps
from app.extensions import db
from app.models import User, book_manager
from werkzeug.exceptions import BadRequest

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_jwt()
        role = token.get('role', None)
        accepted = ['admin' , 'system_admin']
        
        if role in accepted:
            return func(*args, **kwargs)
        else:
            return {'message': 'Access denied'}, 403

    return wrapper
    
def system_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        check = db.session.query(User).filter_by(id=user_id,
            role='system_admin').scalar()

        if check:
            return func(*args, **kwargs)
        else:
            return {'message': 'Access denied'}, 403

    return wrapper

def json_required(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			json_data = request.get_json()
			if json_data is None:
				return {"message" : "Valid JSON required."}, 400
		except BadRequest:
			return {"message" : "Valid JSON required."}, 400

		kwargs["data"] = json_data 
		return func(*args, **kwargs)

	return wrapper