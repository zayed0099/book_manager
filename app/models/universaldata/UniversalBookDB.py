# UniversalBookDB.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class UnivBookDB(db.Model):
	__tablename__ = 'UnivBookDB'

	id = db.Column(db.Integer, primary_key=True)

	title = db.Column(db.String(200), nullable=False)
	normalized_title = db.Column(db.String(200), 
		unique=True, nullable=False, index=True)
	subtitle = db.Column(db.String(200), default=None ,nullable=True)

	category1 = db.Column(db.String(30), 
		nullable=False)
	category1_normal = db.Column(db.String(200), 
		nullable=False, index=True)

	category2 = db.Column(db.String(30), nullable=True)
	category2_normal = db.Column(db.String(200), 
		nullable=True, index=True)

	description = db.Column(db.Text, nullable=True)

	isbn1 = db.Column(db.String(200), default=None, nullable=True)
	isbn2 = db.Column(db.String(200), nullable=True)

	imagelink = db.Column(db.String(250), nullable=False)

	publisher = db.Column(db.String(200), default="unknown", nullable=False)
	publisher_normal = db.Column(db.String(200), 
		nullable=True, default="unknown", index=True)

	pub_date = db.Column(db.String(25), nullable=True)
	page_count = db.Column(db.Integer, nullable=True)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, 
		default=datetime.utcnow, onupdate=datetime.utcnow)

	language = db.Column(db.String(10), nullable=True)
	status = db.Column(db.String(100), default="public", nullable=False)

	# Foreign KEY from author table
	author_id = db.Column(db.Integer, 
		db.ForeignKey('UnivAuthorDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	__table_args__ = (
	db.UniqueConstraint('isbn1', name='uq_isbn1'),
	db.UniqueConstraint('isbn2', name='uq_isbn2'),
	CheckConstraint(
		"status IN ('public' , 'archive')", 
		name='status_validate'),
	)