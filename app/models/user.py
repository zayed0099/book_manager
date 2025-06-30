from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user_db'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    joined = db.Column(db.DateTime, nullable=False)
	role = db.Column(db.String(20), default="user", nullable=False)
	is_banned = db.Column(db.Boolean, default=False, nullable=False)

    books = db.relationship('book_manager', backref='user', lazy=True)