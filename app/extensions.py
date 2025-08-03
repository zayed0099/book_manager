# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# Local Import
from app.schema import (BookSchema
    ,UserSchema
    ,AdminBookSchema
    ,AdminUserSchema
    ,AdminUserSchema_min
    ,ReviewBookSchema
    ,TagSchema
    ,ListDataSchema, 
    BookListSchema)

# Schema instances
book_schema = BookSchema() # for a single book
books_schema = BookSchema(many=True) # for multiple books
user_schema = UserSchema(many=False)
admin_schema_book = AdminBookSchema(many=True)
admin_schema = AdminUserSchema(many=True)
admin_nomail_schema = AdminUserSchema_min(many=True)
review_schema = ReviewBookSchema()
tagschema = TagSchema()
listdataschema = ListDataSchema()
booklistschema = BookListSchema()

# Global instances
db = SQLAlchemy()
migrate = Migrate()


    