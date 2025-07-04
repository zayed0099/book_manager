from flask_restful import Resource, request, abort
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
import random
import string

# Local Import
from app.extensions import (
    db, user_schema, books_schema, book_schema)
from app.models import User, book_manager, jwt_blacklist
from app.errors.handlers import CustomBadRequest
from app.jwt_extensions import jwt, admin_required, limiter, admin_required
from app.logging.ext_admin import logging, logger
'''
admin can see how manu users in there. 
add new admin.
look how many books there are. who has how many books.
ban/mute a user
control flow of all new user joining/account deletion
'''

# A route to get all the admin info and ban/unban them
class Admin_Crud(Resource):
    # Getting info of all admins
    @jwt_required()
    @admin_required()
    @limiter.limit("3 per day")
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        pagination = User.query.filter(User.role == 'admin'
            ,User.is_banned == False).paginate(
            page=page, per_page=per_page, error_out=False)

        if not pagination.items:
            abort(404, description="No admins found.")

        else:
            admins =  user_schema.dump(pagination.items, many=True)

            logger.info('Admin requested to see data of all admins.')
            return {
            'admins': admins,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages
            }, 200
    
    # Adding new admin. (full new user)
    @jwt_required()
    @admin_required()
    @limiter.limit("3 per day")
    def post(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_new_admin = data.get("username")
        pass_new_admin = data.get("password")
        now = datetime.now(timezone.utc)

        if not username_new_admin or not pass_new_admin:
            raise CustomBadRequest("Username and password required.")

        else:
            check_user = User.query.filter(User.username == username_new_admin).first()

            if check_user:
                return {'message' : 'User already exists. Change his role to admin with a put req.'}
            else:
                new_hashed_pw_admin = generate_password_hash(pass_new_admin)

                new_admin = User(username=username_new_admin
                    ,password=new_hashed_pw_admin
                    ,joined=now
                    ,role='admin')

                try:
                    db.session.add(new_admin)
                    db.session.commit()
                    logger.info(f'{username_new_admin} has been added as new admin')
                    return {"Successful": "Head to '/login' to login and start using the api."}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e

    # Upgrading User -> admin
    @jwt_required()
    @admin_required()
    @limiter.limit("3 per day")
    def put(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_of_user = data.get("username")

        if not username_of_user:
            raise CustomBadRequest("Username required.")

        else:
            check_user = User.query.filter(User.username == username_of_user).first()

            if not check_user:
                abort(404, description="User not found in the database.")

            else:
                try:
                    check_user.role = 'admin'
                    db.session.commit()
                    return {'message' : 'User added as admin successfully'}
                    logger.info(f'{username_of_user} : promoted to user -> Admin')
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e


    # removing someone from admin
    @jwt_required()
    @admin_required()
    @limiter.limit("3 per day")
    def delete(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_of_user = data.get("username")

        if not username_of_user:
            raise CustomBadRequest("Username required.")

        else:
            check_user = User.query.filter(User.username == username_of_user
                ,User.role == 'admin').first()

            if not check_user:
                return {'message' : 'User is not an admin.'}

            else:
                try:
                    check_user.role = 'user'
                    db.session.commit()
                    logger.info(f'{username_of_user} has been removed from admin.')
                    return {'message' : 'User removed from admin. Go to /user/ban to ban him from being a user too.'}
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e

class Admin_Book_Manage(Resource):
    # admin wanting to see all the books in the db regardless of user
    @jwt_required()
    @admin_required()
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        title_get = request.args.get('title', '', type=str)
        author = request.args.get('author', '', type=str)

        title = title_get.strip().lower()

        # admin can generally see all the books + only user specific books too.
        user_id = request.args.get('user_id', default=None, type=int)
        
        sort_query = request.args.get('sort', default=None, type=str)
        order = request.args.get('order', 'asc', type=str)


        if user_id is not None:
            filters = [book_manager.is_deleted == False
            ,book_manager.user_id == user_id]
            filt = []
        else:
            filters = [book_manager.is_deleted == False]
            filt = []

        if title and author:
            filters.append(book_manager.normalized_title == title)
            filters.append(book_manager.author == author)
        
        elif author:
            filters.append(book_manager.author == author)
            if sort_query == 'author' and order == 'desc':
                filt = [book_manager.author.desc()]
            elif sort_query == 'author':
                filt = [book_manager.author.asc()]
            

        elif title:
            filters.append(book_manager.normalized_title == title)      
            if sort_query == 'title' and order == 'desc':
                filt = [book_manager.title.desc()]
            elif sort_query == 'title':
                filt = [book_manager.title.asc()]
            


        if sort_query is None:
            pagination = book_manager.query.filter(*filters).paginate(
            page=page, per_page=per_page, error_out=False)
        else:
            pagination = book_manager.query.filter(*filters).order_by(
                *filt).paginate(
                page=page, per_page=per_page, error_out=False)


        if not pagination.items:
            abort(404, description="Book not found.")

        else:
            books =  books_schema.dump(pagination.items)

            logger.info('Admin asked to see all book data.')
            return {
            'user_id' : user_id,
            'books': books,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages
            }, 200

class User_Control(Resource):
    # banning a user from the api.
    @jwt_required()
    @admin_required()
    def delete(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_of_user = data.get("username")

        if not username_of_user:
            raise CustomBadRequest("Username required.")

        else:
            check_user = User.query.filter(User.username == username_of_user).first()

            if not check_user:
                return {'message' : 'User not found.'}

            else:
                try:
                    check_user.is_banned = True
                    db.session.commit()
                    logger.info(f'User [{username_of_user}] has been banned.')
                    return {'message' : f'User [{username_of_user}] has been banned.'}
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e

    # Unbanning a user from the api.
    @jwt_required()
    @admin_required()
    def put(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_of_user = data.get("username")

        if not username_of_user:
            raise CustomBadRequest("Username required.")
        else:
            check_user = User.query.filter(User.username == username_of_user).first()

            if not check_user:
                return {'message' : 'User not found.'}

            else:
                try:
                    check_user.is_banned = False
                    db.session.commit()
                    logger.info(f'User [{username_of_user}] has been unbanned.')
                    return {'message' : f"Access for user '{username_of_user}' has been restored."}
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e             

    @jwt_required()
    @admin_required()
    def post(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_of_user = data.get("username")
        email = data.get('email')

        if not username_of_user and email:
            raise CustomBadRequest("Username and Email both required.")

        else:
            check_user = User.query.filter(User.username == username_of_user, email == email)

            if not check_user:
                return {'message' : 'User not found.'}

            else:
                random_string = ''.join(random.choice(string.ascii_letters) for _ in range(10))

                check_user.password = random_string
                try:
                    db.session.commit()
                    logger.info(f'User [{username_of_user}] password has been changed..')
                    return {'message' : f"Password for user '{username_of_user}' is : {random_string}"}
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e


class Jwt_Manage(Resource):
    # Deleting all old jwt token from the db.
    @jwt_required()
    @admin_required()
    def delete(self):
        now = datetime.now(timezone.utc)

        for token in jwt_blacklist.query.all():
            if now >= (token.created_at + timedelta(days=15)):
                try:
                    db.session.delete(token)
                    db.session.commit()
                    logger.info("JWT token blacklist database has been cleared.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e                
