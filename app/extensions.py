# extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_migrate import Migrate
from argon2 import PasswordHasher

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
    DelRequestGET,
    JSONExportSchema,
    TagSchemaGET)

# Schema instances
book_schema = BookSchema() # for a single book
books_schema = BookSchema(many=True) # for multiple books

user_schema = UserSchema(many=False)

admin_schema_book = AdminBookSchema(many=True)
admin_schema = AdminUserSchema(many=True)
admin_nomail_schema = AdminUserSchema_min(many=True)

review_schema = ReviewBookSchema()

tagschema = TagSchema()
gettagschema = TagSchemaGET()

listdataschema = ListDataSchema()
booklistschema = BookListSchema()

deluserPschema = DelRequestPOST(many=False)
deluserGschema = DelRequestGET(many=False)

exportschema = JSONExportSchema(many=True)


# Global instances
db = SQLAlchemy()
migrate = Migrate()
ph = PasswordHasher()

# Enable foreign keys for SQLite
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    