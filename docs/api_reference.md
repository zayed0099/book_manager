# Book Manager API
   
## API Endpoints

### Authentication
- `POST /auth/v1/register` - Register a new user  
    **Request body:**  
    ```json
    {
        "username": "string (required)",
        "password": "string (required)",
        "email": "string (required)"
    }
    ```  
    **Response:**  
    - 201 Created  
    - 409 Conflict (User already exists)

- `POST /auth/v1/login` - Login and get JWT tokens  
    **Request body:**  
    ```json
    {
        "username": "string (required)",
        "password": "string (required)"
    }
    ```  
    **Response:**  
    - 200 OK (Login successful)  
    - 401 Unauthorized (Incorrect username/password)  
    - 404 Not Found (User not found or banned)

- `POST /auth/v1/refresh` - Refresh access token  
    **Request:**  
    - No request body required  
    - Must include valid refresh token in headers (`Authorization: Bearer <token>`)  

    **Response:**  
    ```json
    {
        "access_token": "newly_generated_token"
    }
    ```

- `DELETE /auth/v1/logout` - Logout and blacklist token  
    **Request:**  
    - No request body required  
    - Must include valid access token in headers (`Authorization: Bearer <token>`)  

    **Response:**  
    - 204 No Content

- `DELETE /auth/user/delete` - Submit user account deletion request  
    **Request:**  
    - Must include valid access token in headers (`Authorization: Bearer <token>`)  
    ```json
    {
        "note": "string (optional)"
    }
    ```  
    **Response:**  
    - 200 OK (Request submitted)  
    - 400 Bad Request (User already has an existing delete request)

- `PUT /auth/user/delete` - Revoke user account deletion request  
    **Request:**  
    - No request body required  
    - Must include valid access token in headers (`Authorization: Bearer <token>`)  

    **Response:**  
    - 200 OK (Request revoked)  
    - 404 Not Found (No existing request found)

### Books
- `GET /api/v1/books` - Get all books (with pagination, search, filters)  
    **Response:** 200 OK (Paginated list of books)

- `POST /api/v1/books` - Create a new book  
    **Request body:**  
    ```json
    {
        "title": "string (required)",
        "author": "string (required)",
        "genre": "string (optional)"
    }
    ```  
    **Response:**  
    - 201 Created  
    - 400 Bad Request

- `GET /api/v1/books/{id}` - Get a specific book  
    **Response:**  
    - 200 OK (Book details)  
    - 404 Not Found

- `PATCH /api/v1/books/{id}` - Update a book  
    **Request body:**  
    ```json
    {
        "title": "string (optional)",
        "author": "string (optional)",
        "genre": "string (optional)"
    }
    ```  
    **Response:**  
    - 200 OK (Book updated)  
    - 404 Not Found

- `DELETE /api/v1/books/{id}` - Soft delete a book  
    **Response:**  
    - 200 OK (Book deleted)  
    - 404 Not Found

- `GET /api/v1/recovery` - Get soft-deleted books  
    **Response:** 200 OK (List of deleted books)

- `GET /api/v1/favourites` - Get favorite books  
    **Response:** 200 OK (List of favorite books)

- `PUT /api/v1/favourites/{id}` - Add book to favorites  
    **Response:**  
    - 200 OK  
    - 404 Not Found

- `DELETE /api/v1/favourites/{id}` - Remove book from favorites  
    **Response:**  
    - 200 OK  
    - 404 Not Found

### Admin Routes  
*Admin-only routes.*

- `GET /a/v1/manage` - Get all admins  
    **Response:** 200 OK

- `GET /a/v1/books` - View all books  
    **Response:** 200 OK

- `PUT /a/v1/user/ban/{id}` - Unban user  
    **Response:**  
    - 200 OK  
    - 404 Not Found

- `DELETE /a/v1/user/ban/{id}` - Ban user  
    **Response:**  
    - 200 OK  
    - 404 Not Found

- `GET /a/v1/user/view` - View all users  
    **Response:** 200 OK

- `DELETE /a/v1/jwt/clear` - Clear expired JWT tokens  
    **Response:** 200 OK

- `DELETE /a/v1/book/clear` - Permanently clear all soft-deleted books (after 30 days)  
    **Response:** 200 OK

*System-Admin only routes.*
- `POST /a/v1/manage` - Create new admin  
    **Request body:**  
    ```json
    {
        "username": "string (required)",
        "password": "string (required)",
        "email": "string (required)"
    }
    ```  
    **Response:**  
    - 201 Created  
    - 409 Conflict (Admin already exists)

- `PUT /a/v1/manage/{id}` - Promote user to admin  
    **Response:**  
    - 200 OK  
    - 404 Not Found

- `DELETE /a/v1/manage/{id}` - Demote admin to user  
    **Response:**  
    - 200 OK  
    - 404 Not Found

- `POST /a/v1/user/reset` - Reset user password  
    **Request body:**  
    ```json
    {
        "email": "string (required)",
        "username" : "string (required)",
        "new_password": "string (required)"
    }
    ```  
    **Response:**  
    - 200 OK  
    - 404 Not Found