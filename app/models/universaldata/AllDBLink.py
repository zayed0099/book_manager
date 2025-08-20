# BookAuthorLink.py
from app.extensions import db
from sqlalchemy import CheckConstraint
from datetime import datetime

class BookAuthorLink(db.Model):
	__tablename__ = "BookAuthorLink"

	id = db.Column(db.Integer, primary_key=True)

	book_id = db.Column(db.Integer, 
		db.ForeignKey('UnivBookDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	author_id = db.Column(db.Integer, 
		db.ForeignKey('UnivAuthorDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	status = db.Column(db.String(100), default="public", nullable=False)

	__table_args__ = (
	db.UniqueConstraint('book_id', 'author_id', name='uq_book_author'),
	CheckConstraint(
		"status IN ('public' , 'archive')", 
		name='status_validate'),
	)

class BookPublLink(db.Model):
	__tablename__ = "BookPublLink"

	id = db.Column(db.Integer, primary_key=True)

	book_id = db.Column(db.Integer, 
		db.ForeignKey('UnivBookDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	publisher_id = db.Column(db.Integer, 
		db.ForeignKey('UnivPubDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	status = db.Column(db.String(100), default="public", nullable=False)

	__table_args__ = (
	db.UniqueConstraint('book_id', 'publisher_id', name='uq_book_author'),
	CheckConstraint(
		"status IN ('public' , 'archive')", 
		name='status_validate'),
	)

class BookCatlLink(db.Model):
	__tablename__ = "BookCatlLink"

	id = db.Column(db.Integer, primary_key=True)

	book_id = db.Column(db.Integer, 
		db.ForeignKey('UnivCatDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	publisher_id = db.Column(db.Integer, 
		db.ForeignKey('UnivPubDB.id', ondelete='CASCADE'), 
		index=True, nullable=False)

	status = db.Column(db.String(100), default="public", nullable=False)

	__table_args__ = (
	db.UniqueConstraint('book_id', 'publisher_id', name='uq_book_author'),
	CheckConstraint(
		"status IN ('public' , 'archive')", 
		name='status_validate'),
	)