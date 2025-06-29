from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.schema import BookSchema, UserSchema
from flask_limiter import Limiter

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
