# book.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class review_tags(db.Model):
	__tablename__ = 'review_tags'

	id = db.Column(db.Integer, primary_key=True)
	tag = db.Column(db.String(100), nullable=False)
	normaliazed_tag = db.Column(db.String(100), nullable=False, index=True)
	
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow)

	# Foreign Keys
	user_id = db.Column(db.Integer, 
		db.ForeignKey('user_db.id', ondelete='CASCADE'), 
		index=True, nullable=False)
	
	review_id = db.Column(db.Integer, 
		db.ForeignKey('RatingsReviews.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	__table_args__ = (
		db.UniqueConstraint('normaliazed_tag' , 'review_id' , name='uq_tag_review'),
		)