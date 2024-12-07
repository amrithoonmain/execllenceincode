from flask import Flask, jsonify, request, send_from_directory, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask import session
import mysql.connector
import os
import sys
from jwt_utils import generate_token, verify_token

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the absolute path to the directory containing the executable
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = sys._MEIPASS
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Connect to the MySQL database with error handling
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="library",
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# User model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# User loader
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    if not db:
        return None
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(user[0], user[1], user[2])
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None
    finally:
        cursor.close()
        if db:
            db.close()

# Serve index page
@app.route('/')
def index():
    try:
        return send_from_directory(BASE_DIR, 'index_final.html')
    except Exception as e:
        print(f"Error serving index: {e}")
        return str(e), 500

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(BASE_DIR, filename)
    except Exception as e:
        print(f"Error serving {filename}: {e}")
        return str(e), 500

# API endpoint to get all books
@app.route('/api/books', methods=['GET'])
@login_required
def get_books():
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM books")
        result = cursor.fetchall()
        db.commit()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint to add a book
@app.route('/api/books', methods=['POST'])
@login_required
def add_book():
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        data = request.json
        cursor.execute(
            "INSERT INTO books (bookId, bookName, publicationYear, author) VALUES (%s, %s, %s, %s)",
            (data['bookId'], data['bookName'], data['publicationYear'], data['author'])
        )
        db.commit()
        return jsonify({"message": "Book added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint to search books by keyword
@app.route('/api/books/search', methods=['GET'])
@login_required
def search_books():
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        keyword = request.args.get('keyword')
        cursor.execute("SELECT * FROM books WHERE bookName LIKE %s", ('%' + keyword + '%',))
        result = cursor.fetchall()
        db.commit()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint to get a single book by ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
@login_required
def get_book(book_id):
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM books WHERE bookId = %s", (book_id,))
        result = cursor.fetchone()
        if result:
            return jsonify(result)
        else:
            return jsonify({"error": "Book not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint to update a book
@app.route('/api/books/<int:book_id>', methods=['PUT'])
@login_required
def update_book(book_id):
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        data = request.json
        cursor.execute(
            "UPDATE books SET bookName = %s, publicationYear = %s, author = %s WHERE bookId = %s",
            (data['bookName'], data['publicationYear'], data['author'], book_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"message": "Book updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint to delete a book
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE bookId = %s", (book_id,))
        db.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Book not found"}), 404
        return jsonify({"message": "Book deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint for user registration
@app.route('/api/register', methods=['POST'])
def register():
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        data = request.json
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (data['username'], data['password'])
        )
        db.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint for user login
@app.route('/api/login', methods=['POST'])
def login():
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = db.cursor()
    try:
        data = request.json
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s AND password = %s",
            (data['username'], data['password'])
        )
        user = cursor.fetchone()
        if user:
            user_obj = User(user[0], user[1], user[2])
            token = generate_token(user[0])
            return jsonify({"message": "User logged in successfully!", "token": token}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        if db:
            db.close()

# API endpoint for user logout
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.pop('token', None)
    return jsonify({"message": "User logged out successfully!"}), 200

# API endpoint to borrow a book
@app.route('/api/books/<int:book_id>/borrow', methods=['POST'])
@login_required
def borrow_book(book_id):
    db = get_db_connection
