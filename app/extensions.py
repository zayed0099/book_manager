from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_jwt
from app.schema import BookSchema, UserSchema
from flask_limiter import Limiter
from app.models.blacklist import jwt_blacklist
from app.models.user import User
from functools import wraps

# Schema instances
book_schema = BookSchema() # for a single book
books_schema = BookSchema(many=True) # for multiple books
user_schema = UserSchema(many=False)

# Function to get user identifier
def get_user_identifier():
    try:
        verify_jwt_in_request(optional=True)
        return str(get_jwt_identity() or get_remote_address())
    except Exception:
        return get_remote_address()

# Global instances
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func = get_user_identifier,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"    
    )

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload['jti']
    token = db.session.query(jwt_blacklist.id).filter_by(jti=jti).scalar()

    return token is not None
# "Return True (i.e., token is revoked) only if we found the token in the blocklist."

def admin_required(func):
	@wraps(func)
    def wrapper(*args, **kwargs):
		token = get_jwt()
        role = token.get('role', None)

        if role == 'admin':
            return func(*args, **kwargs)
        else:
            return {'message': 'Access denied'}, 403

	return wrapper
	