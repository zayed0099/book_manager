from app.extensions import db

class book_manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    normalized_title = db.Column(db.String(200), nullable=False, index=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    favourite = db.Column(db.Boolean, default=False, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user_db.id'), index=True, nullable=False)

    __table_args__ = (
    db.UniqueConstraint('user_id', 'normalized_title', name='uq_user_title_normalized'),
    )