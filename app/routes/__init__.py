from .auth_routes import auth_bp
from .book_routes import book_bp
from .admin_routes import admin_bp
from .export_routes import export_bp
from .dashboard_routes import dashboard_bp

# __all__ = ["User","book_manager", "jwt_blacklist", "Ratings_Reviews" , "review_tags"]
__all__ = [
	"auth_bp",
	"book_bp",
	"admin_bp",
	"export_bp",
	"dashboard_bp"
]
