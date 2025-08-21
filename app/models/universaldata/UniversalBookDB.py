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

	isbn1 = db.Column(db.String(200), default=None, nullable=True)
	isbn2 = db.Column(db.String(200), nullable=True)

	imagelink = db.Column(db.String(250), nullable=False)

	pub_date = db.Column(db.String(25), nullable=True)
	page_count = db.Column(db.Integer, nullable=True)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, 
		default=datetime.utcnow, onupdate=datetime.utcnow)

	language = db.Column(db.String(10), nullable=True)

	# Foreign KEY from author table
	univbook_bookauthlink = db.relationship('BookAuthorLink', 
		backref='univbook_authlink',
		passive_deletes=True, 
		lazy=True)

	univbook_bookpublink = db.relationship('BookPublLink', 
		backref='univbook_publink',
		passive_deletes=True, 
		lazy=True)

	univbook_bookcatlink = db.relationship('BookCatLink', 
		backref='univbook_catlink',
		passive_deletes=True, 
		lazy=True)
	
	__table_args__ = (
	db.UniqueConstraint('isbn1', name='uq_isbn1'),
	db.UniqueConstraint('isbn2', name='uq_isbn2'),
	)

'''
backref structure
firstpart_secondpart
firstpart = db name
secondpart = from which db
'''