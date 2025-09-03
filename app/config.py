import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
	SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

class TestDBConfig:
	basedir = os.path.abspath(os.path.dirname(__file__))
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

class ProductionDBConfig:
	SQLALCHEMY_DATABASE_URI = os.environ.get('POSTGRES_DB_URI')

class jwt_config:
	JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=10)