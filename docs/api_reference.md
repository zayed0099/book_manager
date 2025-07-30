
# Book Manager API
   
## API Endpoints

### Authentication
- `POST /auth/v1/register` - Register a new user
- `POST /auth/v1/login` - Login and get JWT tokens
- `POST /auth/v1/refresh` - Refresh access token
- `DELETE /auth/v1/logout` - Logout and blacklist token

### Books
- `GET /api/v1/books` - Get all books (with pagination, search, filters)
- `POST /api/v1/books` - Create a new book
- `GET /api/v1/books/{id}` - Get a specific book
- `PATCH /api/v1/books/{id}` - Update a book
- `DELETE /api/v1/books/{id}` - Delete a book (soft delete)
- `GET /api/v1/recovery` - Get deleted books
- `GET /api/v1/favourites` - Get favorite books
- `PUT /api/v1/favourites/{id}` - Add book to favorites
- `DELETE /api/v1/favourites/{id}` - Remove book from favorites

### Admin Routes 
	*These are all admin only routes.*
- `GET /a/v1/manage` - Get all admins
- `POST /a/v1/manage` - Create new admin
- `PUT /a/v1/manage/{id}` - Promote user to admin
- `DELETE /a/v1/manage/{id}` - Demote admin to user
- `GET /a/v1/books` - View all books
- `PUT /a/v1/user/ban/{id}` - Unban user
- `DELETE /a/v1/user/ban/{id}` - Ban user
- `GET /a/v1/user/view` - View all users
- `POST /a/v1/user/reset` - Reset user password
- `DELETE /a/v1/jwt/clear` - Clear expired JWT tokens
- `DELETE /a/v1/book/clear` - Clear all soft deleted books (after 30 days of deletion)
