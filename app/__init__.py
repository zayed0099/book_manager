from flask import Flask
import os
from flask_restful import Api

# Local Import
from app.errors.handlers import register_error_handlers
from app.routes.auth_routes import auth_bp
from app.routes.book_routes import book_bp
from app.routes.admin_routes import admin_bp
from app.extensions import db
from .config import Config, dbconfig, jwt_config
from app.jwt_extensions import jwt, limiter

def create_app():
    app = Flask(__name__)
    api = Api(app)

    app.config.from_object(Config)
    app.config.from_object(dbconfig)
    app.config.from_object(jwt_config)
    
    limiter.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    from app.models import User, book_manager, jwt_blacklist

    with app.app_context(): # creating all the database tables
        db.create_all()

    register_error_handlers(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(admin_bp)
    
    return app