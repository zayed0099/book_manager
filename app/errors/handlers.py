from flask import abort
from werkzeug.exceptions import BadRequest
import traceback
from sqlalchemy.exc import SQLAlchemyError

class CustomBadRequest(BadRequest):
    def __init__(self, respond):
        self.description = respond
        super().__init__()

def register_error_handlers(app):
    @app.errorhandler(CustomBadRequest)
    def no_data_error(e):
        return {"message": e.description}, 400

    @app.errorhandler(404)
    def data_not_found_error(e):
        return {"message": e.description or "Resource not found."}, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return {"error": "An internal server error occurred."}, 500

    @app.errorhandler(SQLAlchemyError)
    def db_entry_error(e):
        print("SQLAlchemyError:", e)
        traceback.print_exc()  # shows full stack trace
        return {"error": "Failed to save entry to database"}, 500