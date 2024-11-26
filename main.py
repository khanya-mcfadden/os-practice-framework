import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the table is created when the app starts
def init_db():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    # Create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

# Initialize the database when the app starts
def initialize():
    init_db()

@app.context_processor
def inject_user():
    return dict(logged_in=('username' in session))

@app.route('/')
def index():
    return render_template('index.html'), 404


@app.route('/BookingPage', methods=['GET', 'POST'])
def BookingPage_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        course = request.form.get('courses')
        date = request.form.get('date')

        if not course or not date:
            return "Please fill out all fields", 

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        
        # Create bookings table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY,
                course TEXT NOT NULL,
                date TEXT NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')

        try:
            # Insert the booking
            cursor.execute("INSERT INTO bookings (courses, date, username) VALUES (?, ?, ?)",
                         (course, date, session.get('username')))
            connection.commit()
            connection.close()
            return redirect('/booking_confirm')
        except sqlite3.Error:
            connection.close()
            return "Booking failed", 
    
    return render_template('BookingPage.html')

@app.route('/Orderingpage' , methods=['GET', 'POST'])
def Orderingpage_page():
        return render_template('Orderingpage.html'), 404

@app.route('/Order' , methods=['GET', 'POST'])
def Order():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        item = request.form.get('product')
        quantity = request.form.get('quantity')

        if not item or not quantity:
            return "Please fill out all fields", 

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        
        # Create orders table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                item TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')

        try:
            # Insert the order
            cursor.execute("INSERT INTO orders (item, quantity, username) VALUES (?, ?, ?)",
                         (item, quantity, session.get('username')))
            connection.commit()
            connection.close()
            return redirect('/ordering_confirm')
        except sqlite3.Error:
            connection.close()
            return "Order failed", 
    return render_template('/Orderingpage')

@app.route('/test')
def test_page():
    return render_template('test.html'), 404

@app.route('/about')
def about_page():
    return render_template('about.html'), 404

@app.route('/courses')
def get_courses():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT course_id, course_name, course_description FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return render_template('courses_info.html', courses=courses)

@app.route('/confirm')
def confirm():
    return render_template('confirm.html')

@app.route('/booking_confirm')
def booking_confirm():
    return render_template('booking_confirm.html')

@app.route('/ordering_confirm')
def ordering_confirm():
    return render_template('ordering_confirm.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']

    # Verify user exists in database
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    
    # Check if user exists in database
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        connection.close()
        session.pop('username', None)  # Clear invalid session
        return redirect(url_for('login'))

    # Fetch user-specific bookings
    cursor.execute("SELECT courses, date FROM bookings WHERE username = ?", (username,))
    bookings = cursor.fetchall()
    connection.close()

    return render_template('profile.html', username=username, bookings=bookings)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate input lengths
        if len(username) > 200 or len(password) > 200:
            return "Input exceeds character limit", 

        # Check if the user exists in the database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        
        # Modified query to include admin column
        cursor.execute("SELECT username, password, admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        connection.close()

        if user:
            admin = user[2]  # Get admin status
            if admin:
                # For admin accounts, direct password comparison
                if password == user[1]:  # Direct comparison for admin passwords
                    session['username'] = username
                    session['admin'] = True
                    return redirect(url_for('profile'))
            else:
                # For regular users, check hashed password
                if check_password_hash(user[1], password):
                    session['username'] = username
                    session['admin'] = False
                    return redirect(url_for('profile'))
        
        return "Invalid username or password", 

    return render_template('login.html')
@app.route('/Sign-Up', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            return "Please fill out all fields",   # Simple error handling

        # Validate input lengths
        if len(username) > 15 or len(email) > 50 or len(password) > 20:
            return "Input exceeds character limit", 
        if len(username) < 3 or len(email) < 3 or len(password) < 8:
            return "Input is below character limit", 

        # Validate characters in username and email
        if not re.match("^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", username) or not re.match("^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", email) or not re.match("^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", password):
            return "Invalid characters in username, email or password", 

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert user into database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        # Check if the username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            return "Username or email already exists.", 

        try:
            # Insert the user
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            connection.commit()
        except sqlite3.IntegrityError:
            return "User already exists or email is already registered.", 
        finally:
            connection.close()

        # Redirect to confirmation page
        return redirect('/confirm')

    return render_template('Sign-Up.html')


    
@app.route('/health_page')
def health():
    return render_template('health_page.html')


# Error handler for 404
@app.errorhandler(404)
def page_not_found(_):
    app.logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404

@app.route('/theme', methods=['POST'])
def set_theme():
    theme = request.form.get('theme')
    session['theme'] = theme
    return '', 204

@app.context_processor
def inject_theme():
    theme = session.get('theme', 'light')
    return dict(theme=theme)
def inject_user():
    return {
        'is_authenticated': 'username' in session
    }

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            return "Please fill out all fields", 

        if new_password != confirm_password:
            return "New passwords do not match", 

        if len(new_password) < 8 or len(new_password) > 20:
            return "New password must be between 8 and 20 characters", 

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        
        cursor.execute("SELECT password FROM users WHERE username = ?", (session['username'],))
        user = cursor.fetchone()

        if not user or not check_password_hash(user[0], current_password):
            connection.close()
            return "Current password is incorrect", 

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", 
                      (hashed_password, session['username']))
        connection.commit()
        connection.close()

        return render_template('profile.html')

    return render_template('profile.html')

@app.route('/users_info')
def users_info():
    if 'username' not in session or not session.get('admin'):
        return redirect(url_for('login'))
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT username, email FROM users")
    users = cursor.fetchall()
    connection.close()
    return render_template('users_info.html', users=users)
if __name__ == "__main__":
    initialize()
    app.run(debug=True)