from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from datetime import datetime
import json
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(100),
            full_name VARCHAR(100),
            points INTEGER DEFAULT 0,
            issues_reported INTEGER DEFAULT 0,
            issues_resolved INTEGER DEFAULT 0,
            join_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create issues table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'Open',
            location TEXT NOT NULL,
            coordinates JSONB,
            description TEXT NOT NULL,
            reporter VARCHAR(50) NOT NULL,
            upvotes INTEGER DEFAULT 1,
            created_date DATE DEFAULT CURRENT_DATE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by VARCHAR(50),
            FOREIGN KEY (reporter) REFERENCES users(username)
        )
    ''')
    
    # Create admin user if not exists
    cur.execute('''
        INSERT INTO users (username, password, email, full_name, points)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    ''', ('admin', 'admin123', 'admin@civicconnect.com', 'System Administrator', 1000))
    
    conn.commit()
    cur.close()
    conn.close()

# Helper functions
def generate_unique_id():
    """Generate unique issue ID"""
    import time
    import random
    import string
    timestamp = str(int(time.time() * 1000))[-8:]
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"ISSUE-{timestamp}-{random_part}"

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    from math import radians, cos, sin, asin, sqrt
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def get_address_from_coordinates(lat, lon):
    """Get address from coordinates using Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        response = requests.get(url)
        data = response.json()
        return data.get('display_name', f"{lat}, {lon}")
    except:
        return f"{lat}, {lon}"

# API Routes

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    full_name = data.get('fullName')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            INSERT INTO users (username, password, email, full_name)
            VALUES (%s, %s, %s, %s)
        ''', (username, password, email, full_name))
        conn.commit()
        return jsonify({"success": True, "message": "User registered successfully"})
    except psycopg2.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists"}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """User login"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('isAdmin', False)
    
    # Admin login check
    if is_admin and username == 'admin' and password == 'admin123':
        return jsonify({
            "success": True, 
            "user": {"username": "admin", "type": "admin"}
        })
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    user = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if user:
        return jsonify({
            "success": True,
            "user": {
                "username": user['username'],
                "email": user['email'],
                "fullName": user['full_name'],
                "type": "user"
            }
        })
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/issues', methods=['GET'])
def get_issues():
    """Get all issues with optional filtering"""
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = 'SELECT * FROM issues WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = %s'
        params.append(category)
    
    if status:
        query += ' AND status = %s'
        params.append(status)
    
    query += ' ORDER BY created_date DESC'
    
    cur.execute(query, params)
    issues = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([dict(issue) for issue in issues])

@app.route('/api/issues', methods=['POST'])
def create_issue():
    """Create a new issue"""
    data = request.json
    title = data.get('title')
    category = data.get('category')
    location = data.get('location')
    description = data.get('description')
    reporter = data.get('reporter')
    coordinates = data.get('coordinates')
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Check for similar issues (within 100m and same category)
    similar_issues = []
    if coordinates:
        cur.execute('''
            SELECT * FROM issues 
            WHERE category = %s AND coordinates IS NOT NULL
        ''', (category,))
        all_issues = cur.fetchall()
        
        for issue in all_issues:
            if issue['coordinates']:
                issue_coords = issue['coordinates']
                distance = calculate_distance(
                    coordinates['lat'], coordinates['lon'],
                    issue_coords['lat'], issue_coords['lon']
                )
                if distance < 0.1:  # Within 100 meters
                    similar_issues.append(dict(issue))
    
    if similar_issues:
        return jsonify({
            "success": False, 
            "duplicate": True, 
            "similar_issue": similar_issues[0]
        })
    
    # Create new issue
    issue_id = generate_unique_id()
    cur.execute('''
        INSERT INTO issues (id, title, category, location, description, reporter, coordinates)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (issue_id, title, category, location, description, reporter, json.dumps(coordinates) if coordinates else None))
    
    # Update user stats
    cur.execute('''
        UPDATE users SET issues_reported = issues_reported + 1, points = points + 20
        WHERE username = %s
    ''', (reporter,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True, "issue_id": issue_id, "points_earned": 20})

@app.route('/api/issues/<issue_id>/upvote', methods=['POST'])
def upvote_issue(issue_id):
    """Upvote an issue"""
    data = request.json
    user = data.get('user')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE issues SET upvotes = upvotes + 1 WHERE id = %s', (issue_id,))
    cur.execute('UPDATE users SET points = points + 5 WHERE username = %s', (user,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True, "points_earned": 5})

@app.route('/api/issues/<issue_id>/duplicate-upvote', methods=['POST'])
def upvote_duplicate_issue(issue_id):
    """Upvote a similar existing issue instead of creating duplicate"""
    data = request.json
    user = data.get('user')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE issues SET upvotes = upvotes + 1 WHERE id = %s', (issue_id,))
    cur.execute('UPDATE users SET points = points + 10 WHERE username = %s', (user,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True, "points_earned": 10})

@app.route('/api/issues/<issue_id>/status', methods=['PUT'])
def update_issue_status(issue_id):
    """Update issue status (Admin only)"""
    data = request.json
    status = data.get('status')
    updated_by = data.get('updated_by')
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Get issue details
    cur.execute('SELECT * FROM issues WHERE id = %s', (issue_id,))
    issue = cur.fetchone()
    
    if not issue:
        return jsonify({"success": False, "message": "Issue not found"}), 404
    
    old_status = issue['status']
    
    # Update issue status
    cur.execute('''
        UPDATE issues 
        SET status = %s, last_updated = CURRENT_TIMESTAMP, updated_by = %s 
        WHERE id = %s
    ''', (status, updated_by, issue_id))
    
    # Award bonus points if issue is resolved
    if status == 'Resolved' and old_status != 'Resolved':
        cur.execute('''
            UPDATE users 
            SET points = points + 30, issues_resolved = issues_resolved + 1 
            WHERE username = %s
        ''', (issue['reporter'],))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/api/users/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get user leaderboard"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute('''
        SELECT username, points, issues_reported, issues_resolved, join_date
        FROM users 
        WHERE username != 'admin'
        ORDER BY points DESC
    ''')
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([dict(user) for user in users])

@app.route('/api/users/<username>/stats', methods=['GET'])
def get_user_stats(username):
    """Get user statistics"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute('''
        SELECT points, issues_reported, issues_resolved,
        (SELECT COUNT(*) FROM users WHERE points > u.points) + 1 as rank
        FROM users u WHERE username = %s
    ''', (username,))
    stats = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if stats:
        return jsonify(dict(stats))
    else:
        return jsonify({"points": 0, "issues_reported": 0, "issues_resolved": 0, "rank": "-"})

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute('SELECT COUNT(*) as total FROM issues')
    total_issues = cur.fetchone()['total']
    
    cur.execute('SELECT COUNT(*) as open FROM issues WHERE status = %s', ('Open',))
    open_issues = cur.fetchone()['open']
    
    cur.execute('SELECT COUNT(*) as resolved FROM issues WHERE status = %s', ('Resolved',))
    resolved_issues = cur.fetchone()['resolved']
    
    cur.execute('SELECT COUNT(*) as active FROM users WHERE username != %s', ('admin',))
    active_users = cur.fetchone()['active']
    
    cur.close()
    conn.close()
    
    return jsonify({
        "total_issues": total_issues,
        "open_issues": open_issues,
        "resolved_issues": resolved_issues,
        "active_users": active_users
    })

@app.route('/')
def serve_frontend_root():
    """Serve the main HTML file from the root path"""
    return send_from_directory(os.path.abspath('.'), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve other files from the static directory"""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    # Initialize tables
    init_database()
    
    # Debugging: test database connection
    print("DATABASE_URL from .env:", os.getenv("DATABASE_URL"))
    try:
        # Use psycopg2 to test the connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version_info = cur.fetchone()
        print("✅ Database connected:", version_info[0])
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Database connection failed:", e)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
