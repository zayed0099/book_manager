from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.schema.book_schema import BookSchema
from app.schema.user_schema import UserSchema
from flask_limiter import Limiter

# Schema instances
book_schema = BookSchema() # for a single book
books_schema = BookSchema(many=True) # for multiple books
user_schema = UserSchema(many=False)

# Global instances
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(
    key_func = get_user_identifier,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"    
    )
