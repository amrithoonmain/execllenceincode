from flask import Flask, jsonify, request, send_from_directory, render_template
import mysql.connector
import pyfiglet
import os
import sys

app = Flask(__name__)

# Get the absolute path to the directory containing the executable
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Configure static files path
static_folder = os.path.join(application_path, 'static')
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# Copy static files if running as executable
if getattr(sys, 'frozen', False):
    for filename in ['index_final.html', 'styles.css', 'script_new.js']:
        source = os.path.join(sys._MEIPASS, filename)
        destination = os.path.join(static_folder, filename)
        if os.path.exists(source):
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                dst.write(src.read())

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

# Serve static files
@app.route('/')
def index():
    try:
        return send_from_directory(static_folder, 'index_final.html')
    except Exception as e:
        print(f"Error serving index: {e}")
        return str(e), 500

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(static_folder, filename)
    except Exception as e:
        print(f"Error serving {filename}: {e}")
        return str(e), 500

# API endpoint to get all books
@app.route('/api/books', methods=['GET'])
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
        db.close()

# API endpoint to add a book
@app.route('/api/books', methods=['POST'])
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
        db.close()

# API endpoint to search books by keyword
@app.route('/api/books/search', methods=['GET'])
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
        db.close()

# API endpoint to get a single book by ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
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
        db.close()

# API endpoint to update a book
@app.route('/api/books/<int:book_id>', methods=['PUT'])
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
        db.close()

# API endpoint to delete a book
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
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
        db.close()

if __name__ == '__main__':
    print("\nStarting Digital Library Application...")
    print("Please ensure MySQL server is running on localhost")
    print("Access the application at http://127.0.0.1:5000")
    print(f"Static files will be served from: {static_folder}")
    
    # Run the application
    app.run(debug=False, host='127.0.0.1', port=5000)
