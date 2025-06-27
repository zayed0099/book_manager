from app import db

class jwt_blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(300), nullable=False) # jti → Stands for JWT ID
    ttype = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)   
    user_id_jwt = db.Column(db.Integer, nullable=False)

