# auth.py
from flask_restful import Resource, request, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

# Local Import 
from app.errors.handlers import CustomBadRequest
from app.extensions import db
from app.jwt_extensions import jwt, limiter, admin_required

class AddUser(Resource):
    @limiter.limit("3 per day")
    def post(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        from app.extensions import user_schema
        errors = user_schema.validate(data)

        if errors:
            raise CustomBadRequest("Validation failed")

        else:
            username_signin = data.get("username")
            pass_txt_signin = data.get("password")
            email_signin = data.get("email")

            now = datetime.now(timezone.utc)

            from app.models import User
            check_user = User.query.filter(User.username == username_signin
                ,User.email == email_signin).first()

            if check_user:
                raise CustomBadRequest("An error occured. Please, Try again")
            else:
                new_hashed_pw_signin = generate_password_hash(pass_txt_signin)

                new_user = User(username=username_signin,
                    password=new_hashed_pw_signin,
                    email=email_signin ,joined=now)

                try:
                    db.session.add(new_user)
                    db.session.commit()
                    return {"Successful": "Head to '/login' to login and start using the api."}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e

# User login class
class Login(Resource):
    @limiter.limit("3 per day")
    def post(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_for_login = data.get("username")
        pass_txt_login = data.get("password")

        if not username_for_login and pass_txt_login:
            raise CustomBadRequest("Validation failed")

        else:
            from app.models import User
            check_user = User.query.filter(
                User.username == username_for_login
                ,User.is_banned == False).first()

            if not check_user:
                abort(404, description="User not found.")

            elif check_user.is_banned:
                abort(404, description="User is banned. Email to user.support@bookroad.com")
            
            else:
                if check_user and check_password_hash(check_user.password , pass_txt_login):
                    access_token = create_access_token(identity=check_user.id
                        ,additional_claims={"role": check_user.role})
                    refresh_token = create_refresh_token(identity=check_user.id
                        ,additional_claims={"role": check_user.role})
                    return {"access_token": access_token, "refresh_token": refresh_token}, 200        
                else:
                    return {"message": "Bad username or password. Login unsuccessful"}, 401

# JWT protected class to only get access token using the refresh token
class Ref_Token(Resource):
    @limiter.limit("10 per day")
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        token = get_jwt()
        jti = token['jti']
        ttype = token["type"]
        now = datetime.now(timezone.utc)
        role = token['role']

        try:
            from app.models import jwt_blacklist

            new_refresh_revoke = jwt_blacklist(jti=jti
                ,ttype=ttype
                ,created_at=now
                ,user_id_jwt=identity
                ,role= role)
            db.session.add(new_refresh_revoke)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

        from app.models import User
        user = db.session.get(User, identity)

        access_token = create_access_token(
            identity=identity
            ,additional_claims={"role": user.role})
        refresh_token = create_refresh_token(
            identity=identity
            ,additional_claims={"role": user.role})
        return {"access_token" : access_token, "refresh_token" : refresh_token}, 200

class Del_Token(Resource):
    @limiter.limit("10 per day")
    @jwt_required()
    def delete(self):
        user_id_jwt = get_jwt_identity()
        token = get_jwt()
        jti = token['jti']
        ttype = token["type"]
        role = token['role']
        now = datetime.now(timezone.utc)
        try:
            from app.models import jwt_blacklist
            new_re = jwt_blacklist(jti=jti
                ,ttype=ttype
                ,created_at=now
                ,user_id_jwt=user_id_jwt
                ,role= role)
            db.session.add(new_re)
            db.session.commit()
            return {"message": "Token revoked successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e


class CheckUser(Resource):
    @jwt_required()
    @limiter.limit("5 per day")
    def get(self):
        return {"message": "Valid", "user_id": get_jwt_identity()}, 200
