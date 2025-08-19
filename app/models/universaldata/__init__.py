from .UniversalBookDB import UnivBookDB
from .UniversalAuthorDB import UnivAuthorDB
from .UniversalPublisherDB import UnivPubDB
from .AllDBLink import BookAuthorLink, BookPublLink

__all__ = [
	"UnivBookDB",
	"UnivAuthorDB",
	"BookAuthorLink",
	"UnivPubDB",
	"BookPublLink"
]