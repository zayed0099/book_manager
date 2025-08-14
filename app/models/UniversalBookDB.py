# UniversalBookDB.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class UnivBookDB(db.Model):
	__tablename__ = 'UnivBookDB'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	normalized_title = db.Column(db.String(200), nullable=False, index=True)
	subtitle = db.Column(db.String(200), nullable=False)
	
	author_1 = db.Column(db.String(200), nullable=False)
	author_2 = db.Column(db.String(200), default=None, nullable=False)
	author_3 = db.Column(db.String(200), default=None, nullable=False)
	author_4 = db.Column(db.String(200), default=None, nullable=False)
	author_5 = db.Column(db.String(200), default=None, nullable=False)
	author_6 = db.Column(db.String(200), default=None, nullable=False)

	categories = db.Column(db.String(30), nullable=True)
	categories_normal = db.Column(db.String(200), nullable=True)

	isbn1 = db.Column(db.String(200), nullable=True)
	isbn2 = db.Column(db.String(200), nullable=True)

	imagelink = db.Column(db.String(250), nullable=True)

	publisher = db.Column(db.String(200), nullable=True)
	pub_date = db.Column(db.Date)
	page_count = db.Column(db.Integer, nullable=True)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	