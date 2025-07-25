# book.py
from app.extensions import db
from sqlalchemy import CheckConstraint

class book_manager(db.Model):
    __tablename__ = 'book_manager'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    normalized_title = db.Column(db.String(200), nullable=False, index=True)
    genre = db.Column(db.String(30), nullable=True)

    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    favourite = db.Column(db.Boolean, default=False, nullable=False)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user_db.id'), index=True, nullable=False)

    # Relationship
    reviews_ratings = db.relationship('RatingsReviews', backref='ratingsbook', lazy=True)

    # Unique constraint to keep books unique
    __table_args__ = (
    db.UniqueConstraint('user_id', 'normalized_title', name='uq_user_title_normalized'),
    )


class Ratings_Reviews(db.Model):
    __tablename__ = 'RatingsReviews'    

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_db.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book_manager.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)

    # Checking users rating if its in (1-10), Adding a combined Index 
    # and Unique constraint so that a user has only one review per book
    __table_args__ = (
    CheckConstraint('rating >=1 and rating <= 10', name='rating_control_1_to_10'),
    db.Index('user_book_index', 'user_id', 'book_id'),
    db.UniqueConstraint('user_id' , 'book_id', name='uq_user_book'),
    )