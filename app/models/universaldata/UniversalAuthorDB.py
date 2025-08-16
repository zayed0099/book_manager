# UniversalAuthorDB.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime


class UnivAuthorDB(Resource):
	__tablename__ = "UnivAuthorDB"

	id = db.Column(db.Integer, primary_key=True)

	author = db.Column(db.String(200), nullable=False)
	author_normal = db.Column(db.String(200), 
		nullable=False, index=True)

	status = db.Column(db.String(100), default="active", nullable=False)

	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, 
		default=datetime.utcnow, onupdate=datetime.utcnow)

	# Relationship with Universal Book DB
	univbook = db.relationship('UnivBookDB', 
		backref='univbook',
		passive_deletes=True, 
		lazy=True)

	__table_args__ = (
	CheckConstraint(
		"status IN ('active' , 'banned' , 'on_hold')", 
		name='status_validate'),
	)