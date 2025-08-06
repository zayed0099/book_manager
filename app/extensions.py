# extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
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
    BookListSchema,
    DelRequestPOST,
    DelRequestGET)

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
deluserP = DelRequestPOST(many=False)
deluserg = DelRequestGET(many=False)

# Global instances
db = SQLAlchemy()
migrate = Migrate()

# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    