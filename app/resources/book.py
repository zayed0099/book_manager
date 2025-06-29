from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError

from app.models.book import book_manager
from app.errors.handlers import CustomBadRequest
from app.extensions import limiter, db, book_schema, books_schema


class Book_CR(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        title_get = request.args.get('title', '', type=str)
        author = request.args.get('author', '', type=str)

        title = title_get.strip().lower()

        current_user_id = get_jwt_identity()
        
        filters = [book_manager.user_id == current_user_id, book_manager.is_deleted == False]

        if title and author:
            filters.append(book_manager.normalized_title == title)
            filters.append(book_manager.author == author)
        elif author:
            filters.append(book_manager.author == author)
        elif title:
            filters.append(book_manager.normalized_title == title)
        
        pagination = book_manager.query.filter(*filters).paginate(
            page=page, per_page=per_page, error_out=False)

        if not pagination.items:
            abort(404, description="Book not found.")

        else:
            books =  books_schema.dump(pagination.items)

            return {
            'books': books,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages
            }, 200

    @jwt_required()
    @limiter.limit("50 per day")
    def post(self):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")
        
        errors = book_schema.validate(data)

        if errors:
            raise CustomBadRequest("Validation failed")

        else:
            title = data.get("title")
            author = data.get("author")

            normalized_title = title.lower().strip()

            del_check = book_manager.query.filter_by(
                user_id=get_jwt_identity()
                , is_deleted=True
                , normalized_title=normalized_title).first() 
            
            if not del_check:
                new_book = book_manager(
                    title=title,
                    author=author,
                    normalized_title=normalized_title,
                    user_id=get_jwt_identity(),
                    is_deleted=False
                )

                try:
                    db.session.add(new_book)
                    db.session.commit()
                    return book_schema.dump(new_book), 201
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e
            else:
                del_check.is_deleted = False
                try:
                    db.session.commit()
                    return {'message' : f"({del_check.title}) is added to the list."}
                except SQLAlchemyError as e:
                    db.session.rollback()
                    raise e

# JWT protected class to update, delete and get book by id.
class Book_RUD(Resource):
    @jwt_required()
    def get(self, id):
        current_user_id = get_jwt_identity()
        book_to_work = book_manager.query.filter_by(user_id=current_user_id, id=id, is_deleted = False).first()        
        
        if not book_to_work:
            abort(404, description="Book not found.")
        else:
            return (book_schema.dump(book_to_work)), 200

    @jwt_required()
    @limiter.limit("50 per day")
    def put(self, id):
        try:
            data = request.get_json()
            if data is None:
                raise CustomBadRequest("Missing JSON in request.")
        except BadRequest:
            raise CustomBadRequest("Invalid JSON format.")
        
        errors = book_schema.validate(data)

        if errors:
            raise CustomBadRequest("Validation failed")
            
        else:
            current_user_id = get_jwt_identity()
            
            book_to_work = book_manager.query.filter_by(user_id=current_user_id, id=id, is_deleted = False).first()
            
            if not book_to_work:
                abort(404, description="Book not found.")

            try:
                book_to_work.title = data['title']
                book_to_work.author = data['author'] 
                db.session.commit()
                return {"message" : "Updated Successfully"}, 200 
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e
    
    @jwt_required()
    @limiter.limit("50 per day")
    def delete(self, id):
        current_user_id = get_jwt_identity()
            
        book_tw = book_manager.query.filter_by(user_id=current_user_id, id=id).first()
        if not book_tw:
            abort(404, description="Book not found.")

        try:    
            book_tw.is_deleted = True
            db.session.commit()
            return {"message" : "Deleted Successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

class Book_reuse(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        pagination = book_manager.query.filter(
            user_id=get_jwt_identity()
            ,is_deleted=True
            ).paginate(
            page=page, per_page=per_page, error_out=False)

        if not pagination.items:
            abort(404, description="Book not found.")

        else:
            books =  books_schema.dump(pagination.items)

            return {
            'books': books,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages
            }, 200
