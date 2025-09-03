# UniversalBookDB.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class UnivBookDB(db.Model):
	__tablename__ = 'UnivBookDB'

	id = db.Column(db.Integer, primary_key=True)

	title = db.Column(db.String(200), nullable=False)
	normalized_title = db.Column(db.String(200), 
		unique=True, 
		nullable=False, 
		index=True)

	subtitle = db.Column(db.String(200), default=None ,nullable=True)

	description = db.Column(db.Text, nullable=True)

	isbn1 = db.Column(db.String(200), 
		default=None, 
		nullable=True,
		unique=True)
	isbn2 = db.Column(db.String(200), 
		nullable=True,
		unique=True)

	imagelink = db.Column(db.String(250), nullable=False)

	pub_date = db.Column(db.String(25), nullable=True)
	page_count = db.Column(db.Integer, nullable=True)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, 
		default=datetime.utcnow, onupdate=datetime.utcnow)

	language = db.Column(db.String(10), nullable=True)

	status = db.Column(db.String(100), default="active", nullable=False)

	# relation from author table
	bookauthlink = db.relationship('BookAuthorLink', 
		backref='univbook_authlink',
		passive_deletes=True, 
		lazy=True)

	bookpublink = db.relationship('BookPublLink', 
		backref='univbook_publink',
		passive_deletes=True, 
		lazy=True)

	bookcatlink = db.relationship('BookCatLink', 
		backref='univbook_catlink',
		passive_deletes=True, 
		lazy=True)

	__table_args__ = (
	CheckConstraint(
		"status IN ('active' , 'banned' , 'on_hold')", 
		name='status_validate'),
	)
'''
backref structure
firstpart_secondpart
firstpart = db name
secondpart = from which db
'''