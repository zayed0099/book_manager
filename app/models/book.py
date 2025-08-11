# book.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class book_manager(db.Model):
    __tablename__ = 'book_manager'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    normalized_title = db.Column(db.String(200), nullable=False, index=True)
    genre = db.Column(db.String(30), nullable=True)
    genre_normal = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(100), server_default="wishlist", nullable=False)

    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    favourite = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key
    user_id = db.Column(db.Integer, 
        db.ForeignKey('user_db.id', ondelete='CASCADE'), 
        index=True, nullable=False)

    # Relationship
    reviews_ratings = db.relationship('Ratings_Reviews', 
        backref='ratingsbook',
        passive_deletes=True, 
        lazy=True)

    # Unique constraint to keep books unique
    # Constraint to limit the status and make it same as marsh schema
    __table_args__ = (
    db.UniqueConstraint('user_id', 'normalized_title', name='uq_user_title_normalized'),
    CheckConstraint(
        "status IN ('wishlist' , 'in_progress' , 'completed' , 'abandoned')", 
        name='status_validate'),
    )

class Ratings_Reviews(db.Model):
    __tablename__ = 'RatingsReviews'    

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, 
        db.ForeignKey('user_db.id', ondelete='CASCADE'),
        index=True, nullable=False)
    book_id = db.Column(db.Integer, 
        db.ForeignKey('book_manager.id', ondelete='CASCADE'), 
        index=True, nullable=False)

    # Relationships
    review_tags = db.relationship('review_tags', 
        backref='tagsbook', 
        passive_deletes=True,
        lazy=True)

    # Checking users rating if its in (1-10), Adding a combined Index 
    # and Unique constraint so that a user has only one review per book
    __table_args__ = (
    CheckConstraint('rating >=1 and rating <= 10', name='rating_control_1_to_10'),
    db.UniqueConstraint('user_id' , 'book_id', name='uq_user_book'),
    )