from flask_restful import Resource, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from sqlalchemy.exc import SQLAlchemyError

# Local Import
from app.errors.handlers import CustomBadRequest
from app.extensions import db, book_schema, books_schema
from app.jwt_extensions import limiter

class Book_CR(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=5, type=int)

        title_get = request.args.get('title', '', type=str)
        author = request.args.get('author', '', type=str)

        title = title_get.strip().lower()

        current_user_id = get_jwt_identity()
        
        genre = request.args.get('genre', default=None, type=str)

        sort_query = request.args.get('sort', default=None, type=str)
        order = request.args.get('order', 'asc', type=str)

        from app.models.book import book_manager
        from app.extensions import books_schema

        filters = [book_manager.user_id == current_user_id, book_manager.is_deleted == False]
        filt = []

        if genre is not None:
            filters.append(book_manager.genre == genre)

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

        from app.extensions import book_schema
        errors = book_schema.validate(data)

        if errors:
            raise CustomBadRequest("Validation failed")

        else:
            title = data.get("title")
            author = data.get("author")
            genre = data.get("genre", None)

            normalized_title = title.lower().strip()

            from app.models.book import book_manager

            del_check = book_manager.query.filter_by(
                user_id=get_jwt_identity()
                , is_deleted=True
                , normalized_title=normalized_title).first() 
            
            if not del_check:
                new_book = book_manager(
                    title = title,
                    author = author,
                    normalized_title = normalized_title,
                    user_id = get_jwt_identity(),
                    is_deleted = False,
                    genre = genre
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
        from app.models.book import book_manager
        from app.extensions import book_schema

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
        
        from app.models.book import book_manager
        from app.extensions import book_schema

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
                book_to_work.normalized_title = data['title'].lower().strip() 
                db.session.commit()
                return {"message" : "Updated Successfully"}, 200 
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e
    
    @jwt_required()
    @limiter.limit("50 per day")
    def delete(self, id):
        current_user_id = get_jwt_identity()
        
        from app.models.book import book_manager
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

        from app.models.book import book_manager
        from app.extensions import books_schema
        
        current_user_id = get_jwt_identity()
        
        pagination = book_manager.query.filter(
            book_manager.user_id == get_jwt_identity(),
            book_manager.is_deleted == True
        ).paginate(page=page, per_page=per_page, error_out=False)


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


class BookRecover(Resource):
    @jwt_required()
    def put(self, id):
        from app.models.book import book_manager
        current_user_id = get_jwt_identity()
        
        check = book_manager.query.filter(
            book_manager.user_id == current_user_id,
            book_manager.id == id).first()
        
        if not check:
            return {"message" : "Book not found"}, 404

        else:
            if check.is_deleted:
                try:
                    check.is_deleted = False
                    db.session.commit()
                    return {'message' : 'Book recovered.'}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'message' : 'An error occured.'}, 404
            else:
                return {'message' : 'Book is already recovered. No need to send another recovery request.'}, 200

class Book_Favourite_get(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        title_get = request.args.get('title', '', type=str)
        author = request.args.get('author', '', type=str)

        title = title_get.strip().lower()

        current_user_id = get_jwt_identity()
        
        sort_query = request.args.get('sort', default=None, type=str)
        order = request.args.get('order', 'asc', type=str)
        
        genre = request.args.get('genre', default=None, type=str)

        from app.models.book import book_manager
        from app.extensions import books_schema
        
        filters = [
            book_manager.user_id == current_user_id,
            book_manager.favourite == True,
            book_manager.is_deleted == False,
        ]

        filt = []

        if genre is not None:
            filters.append(book_manager.genre == genre)

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

            return {
            'favourite books': books,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages
            }, 200

class Book_Favourite_ud(Resource):
    @jwt_required()
    def put(self, id):
        from app.models.book import book_manager
        current_user_id = get_jwt_identity()
        
        check = book_manager.query.filter(
            book_manager.user_id == current_user_id,
            book_manager.id == id).first()
        
        if not check:
            return {"message" : "Book not found"}, 404

        else:
            if check.favourite:
                return {'message' : 'Book already added as favourite.'}, 404

            elif check.is_deleted:
                return {'message' : 'Book deleted. Restore to add as favourite.'}, 400 

            elif not check.favourite:
                try:
                    check.favourite = True
                    db.session.commit()
                    return {'message' : 'Book added as favourite'}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'message' : 'An error occured.'}
                    raise e

    @jwt_required()
    def delete(self, id):
        from app.models.book import book_manager
        
        current_user_id = get_jwt_identity()

        check = book_manager.query.filter(
            book_manager.user_id == current_user_id,
            book_manager.id == id).first()
        
        if not check:
            return {"message" : "Book not found"}

        else:
            if check.is_deleted:
                return {'message' : 'Book already deleted. Head to /api/v1/recovery to restore.'}, 404

            elif check.favourite:
                try:
                    check.favourite = False
                    db.session.commit()
                    return {'message' : 'Book removed from favourites.'}, 200
                except SQLAlchemyError as e:
                    db.session.rollback()
                    return {'message' : 'An error occured.'}, 500
                    raise e
