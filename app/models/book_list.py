# book.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

# Class to store all list name and user_id
class ListOwner(db.Model):
	__tablename__ = 'ListOwner'

	id = db.Column(db.Integer, primary_key=True)	
	user_id = db.Column(db.Integer, 
		db.ForeignKey('user_db.id', ondelete='CASCADE'), 
		index=True, nullable=False)
	list_name = db.Column(db.String(200), nullable=False)
	list_name_norm = db.Column(db.String(200), index=True, nullable=False)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow)
	is_deleted = db.Column(db.Boolean, default=False, nullable=False)

	# Relationships
	list_elements = db.relationship('ListBook', 
		passive_deletes=True,
		backref='list_name', lazy=True)

# class to store books in list with a fk(list id)
class ListBook(db.Model):
	__tablename__ = 'ListBook'

	id = db.Column(db.Integer, primary_key=True)
	list_id = db.Column(db.Integer, 
		db.ForeignKey('ListOwner.id', ondelete='CASCADE'), 
		index=True, nullable=False)
	
	title = db.Column(db.String(200), nullable=False)
	author = db.Column(db.String(200), nullable=False)
	normalized_title = db.Column(db.String(200), nullable=False, index=True)
	genre = db.Column(db.String(30), nullable=True)
	status = db.Column(db.String(100), server_default="wishlist", nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow)
	is_list_deleted = db.Column(db.Boolean, default=False, nullable=False)

	__table_args__ = (
	db.UniqueConstraint('list_id', 'normalized_title', name='uq_user_title_normalized'),
	CheckConstraint(
		"status IN ('wishlist' , 'in_progress' , 'completed' , 'abandoned')", 
		name='status_validate'),
	)
