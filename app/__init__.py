from flask import Flask
import os
from flask_restful import Api
from flask_cors import CORS

# Local Import
from app.errors.handlers import register_error_handlers
from app.extensions import db, migrate
from .config import Config, dbconfig, jwt_config
from app.jwt_extensions import jwt, limiter
from app.ui_routes.admin_routes import admin_ui_bp
from app.ui_routes.user_routes import user_ui_bp
from app.ui_routes.auth_routes import auth_ui_bp


def create_app():
	app = Flask(__name__)
	api = Api(app)

	app.config.from_object(Config)
	app.config.from_object(dbconfig)
	app.config.from_object(jwt_config)
	
	CORS(app)

	limiter.init_app(app)
	db.init_app(app)
	jwt.init_app(app)
	migrate.init_app(app, db)
	
	from app.models import (
		User, 
		book_manager, 
		jwt_blacklist, 
		Ratings_Reviews,
		review_tags,
		ListOwner, 
		ListBook,
		DeleteUser,
		UnivBookDB,
		UnivAuthorDB, 
		BookAuthorLink,
		UnivPubDB,
		BookPublLink,
		BookCatLink,
		UnivCatDB)

	with app.app_context(): # creating all the database tables
		db.create_all()

	from app.routes import (
		auth_bp,
		book_bp,
		admin_bp,
		export_bp,
		dashboard_bp)

	register_error_handlers(app)
	app.register_blueprint(auth_bp)
	app.register_blueprint(book_bp)
	app.register_blueprint(admin_bp)
	app.register_blueprint(export_bp)
	app.register_blueprint(dashboard_bp)
	
	app.register_blueprint(admin_ui_bp)
	app.register_blueprint(user_ui_bp)
	app.register_blueprint(auth_ui_bp)
	

	return app