# user.py
from app.extensions import db
from datetime import datetime
from sqlalchemy import CheckConstraint

class User(db.Model):
    __tablename__ = 'user_db'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    joined = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    was_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    books = db.relationship('book_manager', 
        backref='user', 
        passive_deletes=True, lazy=True)
    
    book_review = db.relationship('Ratings_Reviews', 
        backref='ratingsuser', 
        passive_deletes=True ,lazy=True)
    
    tags = db.relationship('review_tags', 
        backref='tagsuser', 
        passive_deletes=True ,lazy=True)
    
    booklist = db.relationship('ListOwner', 
        backref='userlist', 
        passive_deletes=True ,lazy=True)

    __table_args__ = (
    CheckConstraint(
        "role IN ('user' , 'admin' , 'system_admin')", 
        name='role_validate'),
    )