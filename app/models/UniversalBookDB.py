# UniversalBookDB.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class UnivBookDB(db.Model):
	__tablename__ = 'UnivBookDB'

	id = db.Column(db.Integer, primary_key=True)

	title = db.Column(db.String(200), nullable=False)
	normalized_title = db.Column(db.String(200), 
		nullable=False, index=True)
	subtitle = db.Column(db.String(200), default=None ,nullable=True)
	
	author1 = db.Column(db.String(200), nullable=False)
	author1_normal = db.Column(db.String(200), 
		nullable=False, index=True)

	author2 = db.Column(db.String(200), default=None, nullable=False)
	author2_normal = db.Column(db.String(200), 
		default=None, nullable=False, index=True)

	author3 = db.Column(db.String(200), default=None, nullable=False)
	author4 = db.Column(db.String(200), default=None, nullable=False)
	author5 = db.Column(db.String(200), default=None, nullable=False)

	category1 = db.Column(db.String(30), 
		default=None, nullable=True)
	category1_normal = db.Column(db.String(200), 
		default=None, nullable=True, index=True)

	category2 = db.Column(db.String(30), 
		default=None, nullable=True)
	category2_normal = db.Column(db.String(200), 
		default=None, nullable=True, index=True)

	description = db.Column(db.Text, default=None, nullable=False)

	isbn1 = db.Column(db.String(200), default=None, nullable=False)
	isbn2 = db.Column(db.String(200), default=None, nullable=True)

	imagelink = db.Column(db.String(250), nullable=False)

	publisher = db.Column(db.String(200), nullable=False)
	publisher_normal = db.Column(db.String(200), 
		default=None, nullable=False, index=True)

	pub_date = db.Column(db.Date, default=None, nullable=True)
	page_count = db.Column(db.Integer, default=None, nullable=True)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, 
		default=datetime.utcnow, onupdate=datetime.utcnow)

	status = db.Column(db.String(100), default="public", nullable=False)

	__table_args__ = (
	db.UniqueConstraint('normalized_title', 'author1_normal', name='uq_normalized_title_author'),
	db.UniqueConstraint('isbn1' ,'isbn2', name='uq_isbn'),
	CheckConstraint(
		"status IN ('public' , 'archive')", 
		name='status_validate'),

	)