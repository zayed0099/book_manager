# UniversalCategoryDB.py

from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class UnivCatDB(db.Model):
	__tablename__ = "UnivCatDB"

	id = db.Column(db.Integer, primary_key=True)

	category = db.Column(
		db.String(200), 
		default="uncategorized", 
		nullable=False)
	
	category_normal = db.Column(
		db.String(200), 
		nullable=False, 
		default="uncategorized", 
		index=True,
		unique=True)

	status = db.Column(db.String(100), default="active", nullable=False)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, 
		default=datetime.utcnow, onupdate=datetime.utcnow)

	# Relationship with Universal Book DB
	univcat_catbooklink = db.relationship('BookCatLink', 
		backref='univcat',
		passive_deletes=True, 
		lazy=True)

	__table_args__ = (
	CheckConstraint(
		"status IN ('active' , 'banned' , 'on_hold')", 
		name='status_validate'),
	)