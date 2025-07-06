# extensions.py
from flask_sqlalchemy import SQLAlchemy

# Local Import
from app.schema import BookSchema, UserSchema

# Schema instances
book_schema = BookSchema() # for a single book
books_schema = BookSchema(many=True) # for multiple books
user_schema = UserSchema(many=False)

# Global instances
db = SQLAlchemy()


    