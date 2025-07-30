
# Book Manager API

A Flask-based REST API for managing personal book collections with user authentication, admin controls, and comprehensive book management features.

## Features

### User Management
- **User Registration & Authentication** - JWT-based authentication system
- **Role-based Access Control** - User and Admin roles with different permissions
- **Account Security** - Password hashing, token blacklisting, and ban/unban functionality
- **Rate Limiting** - Built-in rate limiting to prevent abuse

### Book Management
- **CRUD Operations** - Create, Read, Update, Delete books in your collection
- **Search & Filter** - Search by title, author, genre with sorting options
- **Soft Delete** - Books are marked as deleted but can be recovered
- **Favorites System** - Mark books as favorites for quick access
- **Pagination** - Efficient pagination for large collections

### Admin Features
- **User Management** - Ban/unban users, promote users to admin
- **Book Oversight** - View all books across all users
- **Token Management** - Clean up expired JWT tokens
- **Admin Controls** - Full administrative access to the system

## Tech Stack

- **Backend**: Flask, Flask-RESTful
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Security**: Werkzeug password hashing
- **Rate Limiting**: Flask-Limiter

## Getting Started

For setup and installation instructions, see [docs/setup.md](docs/setup.md).

   
## API Endpoints

For API endpoints instructions, see [docs/api_reference.md](docs/api_reference.md).

## Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **JWT Token Management**: Access and refresh tokens with blacklisting
- **Rate Limiting**: Prevents API abuse with configurable limits
- **Input Validation**: Marshmallow schemas validate all inputs
- **Role-based Access**: Admin-only endpoints protected
- **SQL Injection Prevention**: SQLAlchemy ORM protects against SQL injection

## Rate Limiting

Default rate limits:
- **General**: 200 requests per day, 50 per hour
- **Registration**: 3 attempts per day
- **Login**: 3 attempts per day
- **Book operations**: 50 per day


## License

This project is licensed under the MIT License .

## Support

For support, email zayed.ah06@gmail.com or create an issue in the GitHub repository.

## Changelog


### v1.1.0
- Added a basic JavaScript and HTML frontend to consume the API
- Implemented rating and reviews functionality for books
- Improved core logic and fixed various bugs for better stability

### v1.0.0
- Initial release
- User authentication and authorization
- Book CRUD operations
- Admin panel
- Rate limiting
- JWT token management

```
