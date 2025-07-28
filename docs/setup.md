
# Book Manager API

A Flask-based REST API for managing personal book collections with user authentication, admin controls, and comprehensive book management features.

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/book-manager-api.git
   cd book-manager-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

5. **Run the application**
   ```bash
   python run.py
   ```
 