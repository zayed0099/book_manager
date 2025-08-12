from flask import request
from flask_jwt_extended import get_jwt_identity
from app.models.book import book_manager

def get_book_query_params():
    return {
        "page": request.args.get("page", default=1, type=int),
        "per_page": request.args.get("per_page", default=5, type=int),
        "title": request.args.get("title", "", type=str).strip().lower(),
        "author": request.args.get("author", "", type=str),
        "genre": request.args.get("genre", default=None, type=str),
        "sort_query": request.args.get("sort", default=None, type=str),
        "order": request.args.get("order", "asc", type=str),
        "current_user_id": get_jwt_identity()
    }

def book_filters_and_sorting(params):
    filters = [book_manager.is_deleted == False]
    order_by = []

    if params["genre"]:
        filters.append(book_manager.genre == params["genre"])

    if params["title"] and params["author"]:
        filters.append(book_manager.normalized_title == params["title"])
        filters.append(book_manager.author == params["author"])

    elif params["author"]:
        filters.append(book_manager.author == params["author"])
        if params['sort_query'] == 'author' and params['order'] == 'desc':
            order_by = [book_manager.author.desc()]
        elif params['sort_query'] == 'author':
            order_by = [book_manager.author.asc()]

    elif params["title"]:
        filters.append(book_manager.normalized_title == params["title"])
        if params["sort_query"] == "title" and params['order'] == 'desc':
            order_by = [book_manager.title.desc()]
        elif params["sort_query"] == 'title':
            order_by = [book_manager.title.asc()]

    return filters, order_by
