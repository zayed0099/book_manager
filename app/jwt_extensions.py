from flask_jwt_extended import (JWTManager, 
    verify_jwt_in_request, 
    get_jwt_identity, 
    get_jwt)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from app.extensions import db
from app.models import User, jwt_blacklist

jwt = JWTManager()

# Function to get user identifier
def get_user_identifier():
    try:
        verify_jwt_in_request(optional=True)
        return str(get_jwt_identity() or get_remote_address())
    except Exception:
        return get_remote_address()

limiter = Limiter(
    key_func = get_user_identifier,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"    
    )

limiter.enabled = False

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload['jti']
    token = db.session.query(jwt_blacklist.id).filter_by(jti=jti).scalar()

    return token is not None
# "Return True (i.e., token is revoked) only if we found the token in the blocklist."

