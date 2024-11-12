import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for

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

@app.route('/BookingPage')
def BookingPage_page():
    return render_template('BookingPage.html'), 404

@app.route('/Orderingpage')
def Orderingpage_page():
    return render_template('Orderingpage.html'), 404

@app.route('/test')
def test_page():
    return render_template('test.html'), 404

@app.route('/about')
def about_page():
    return render_template('about.html'), 404

@app.route('/courses')
def courses_page():
    return render_template('courses.html'), 404
@app.route('/confirm')
def confirm():
    return render_template('confirm.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        return render_template('profile.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists in the database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            session['username'] = username  # Store username in session
            return redirect(url_for('profile'))
        else:
            return "Invalid username or password", 400

    return render_template('login.html')

@app.route('/Sign-Up', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            return "Please fill out all fields", 400  # Simple error handling

        # Insert user into database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        try:
            # Insert the user
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            connection.commit()
        except sqlite3.IntegrityError:
            return "User already exists or email is already registered.", 400
        finally:
            connection.close()

        # Redirect to confirmation page
        return redirect('/confirm')

    return render_template('Sign-Up.html')

# Error handler for 404
@app.errorhandler(404)
def page_not_found(_):
    app.logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404

@app.route('/admin')
def admin_dashboard():
    if 'admin' in session:
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the admin exists in the database
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND is_admin = 1", (username, password))
        admin = cursor.fetchone()
        connection.close()

        if admin:
            session['admin'] = username  # Store admin username in session
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin username or password", 400

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin',)

if __name__ == "__main__":
    initialize()
    app.run(debug=True)