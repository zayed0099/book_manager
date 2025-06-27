from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from config import Config, dbconfig, jwt_config
from flask_jwt_extended import get_jwt_identity, JWTManager, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from schema.book_schema import BookSchema
from schema.user_schema import UserSchema 
from routes.auth_routes import auth_bp

# Function to get user identifier
def get_user_identifier():
	try:
		verify_jwt_in_request(optional=True)
		return str(get_jwt_identity() or get_remote_address())
	except Exception:
		return get_remote_address()

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


def create_app():
	app = Flask(__name__)
	api = Api(app)

	app.config.from_object(Config)
	app.config.from_object(dbconfig)
	app.config.from_object(jwt_config)
	
	limiter.init_app(app)
	db.init_app(app)
	jwt.init_app(app)

    app.register_blueprint(auth_bp)

	return app