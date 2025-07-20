from flask_restful import Resource, request, abort
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

# Local Import
from app.extensions import db
from app.errors.handlers import CustomBadRequest
from app.jwt_extensions import jwt, admin_required, limiter
from app.logging.ext_admin import logger
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
    @admin_required
    @limiter.limit("3 per day")
    def get(self):
        from app.models import User
        from app.extensions import user_schema

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        pagination = User.query.filter(User.role == 'admin'
            ,User.is_banned == False).paginate(
            page=page, per_page=per_page, error_out=False)

        if not pagination.items:
            abort(404, description="No admins found.")

        else:
            from app.extensions import admin_schema
            admins =  admin_schema.dump(pagination.items, many=True)

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
    @admin_required
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
            username_new_admin = data.get("username")
            pass_new_admin = data.get("password")
            email_new_admin = data.get("email")
            now = datetime.now(timezone.utc)

            from app.models import User
            check_user = User.query.filter(User.username == username_new_admin).first()

            if check_user:
                return {'message' : 'User already exists. Change his role to admin with a put req.'}
            else:
                new_hashed_pw_admin = generate_password_hash(pass_new_admin)

                new_admin = User(username=username_new_admin
                    ,password=new_hashed_pw_admin
                    ,joined=now
                    ,role='admin'
                    ,email=email_new_admin)

                try:
                    db.session.add(new_admin)
                    db.session.commit()
                    logger.info(f'{username_new_admin} has been added as new admin')
                    return {"Successful": "Head to '/login' to login and start using the api."}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e

class AdminUD(Resource):
    # Upgrading User -> admin
    @jwt_required()
    @admin_required
    @limiter.limit("3 per day")
    def put(self, id):
        from app.models import User
        check_user = User.query.filter(User.id == id).first()

        if not check_user:
            abort(404, description="User not found in the database.")

        elif check_user.role == "admin":
            return {"message" : "User already a admin. Send a Delete req to remove."}, 400

        else:
            try:
                check_user.role = 'admin'
                db.session.commit()
                logger.info(f'{check_user.username} : promoted to user -> Admin')
                return {'message' : 'User added as admin successfully'}, 200
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e

    # removing someone from admin
    @jwt_required()
    @admin_required
    @limiter.limit("3 per day")
    def delete(self, id):
        from app.models import User
        check_user = User.query.filter(User.id == id
            ,User.role == 'admin').first()

        if not check_user:
            return {'message' : 'User is not an admin.'}, 404

        else:
            try:
                check_user.role = 'user'
                db.session.commit()
                logger.info(f'{check_user.username} has been removed from admin.')
                return {
                    'message': (
                            "User removed from admin. "
                            "Go to /user/ban to ban the user from using the API."
                        )
                    }, 200
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e

class Admin_Book_Manage(Resource):
    # admin wanting to see all the books in the db regardless of user
    @jwt_required()
    @admin_required
    def get(self):
        from app.models import book_manager

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
            from app.extensions import admin_schema_book
            books =  admin_schema_book.dump(pagination.items)

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
    @admin_required
    def delete(self, id):
        from app.models import User
        check_user = User.query.filter(User.id == id).first()

        if not check_user:
            return {'message' : 'User not found.'}, 404

        try:
            check_user.is_banned = True
            db.session.commit()
            logger.info(f'User [{check_user.username}] has been banned.')
            return {'message' : f'User [{check_user.username}] has been banned.'}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    # Unbanning a user from the api.
    @jwt_required()
    @admin_required
    def put(self, id):
        from app.models import User
        check_user = User.query.filter(User.id == id).first()

        if not check_user:
            return {'message' : 'User not found.'}, 404

        try:
            check_user.is_banned = False
            db.session.commit()
            logger.info(f'User [{check_user.username}] has been unbanned.')
            return {'message' : f"Access for user '{check_user.username}' has been restored."}
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e             

# To reset a users password
class UserCredChange(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")

        username_of_user = data.get("username")
        email = data.get('email')
        new_pass = data.get('password')

        if not username_of_user or not email or not new_pass:
            raise CustomBadRequest("Username, Email, and Password are all required.")

        else:
            check_user = User.query.filter(
                User.username == username_of_user
                ,User.email == email).first()

            if not check_user:
                return {'message' : 'User not found.'}

            check_user.password = generate_password_hash(new_pass)
            try:
                db.session.commit()
                logger.info(f'User [{username_of_user}] password has been changed..')
                return {'message' : f'User [{username_of_user}] password has been changed..'}, 200
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e


class Jwt_Manage(Resource):
    # Deleting all old jwt token from the db.
    @jwt_required()
    @admin_required
    def delete(self):
        from app.models import jwt_blacklist
        now = datetime.now(timezone.utc)

        for token in jwt_blacklist.query.all():
            created_at = token.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            if now >= (created_at + timedelta(days=15)):
                try:
                    db.session.delete(token)
                    db.session.commit()
                    logger.info("JWT token blacklist database has been cleared.")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e                
            else:
                return {"message" : "Jwt tokens are still not permitted to delete."}, 200