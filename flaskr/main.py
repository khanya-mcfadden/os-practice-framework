from datetime import datetime, timedelta
import os
import sqlite3
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import re


app = Flask(__name__)
app.secret_key = "1mads"


# Ensure the table is created when the app starts
def init_db():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    # Create the users table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """
    )
    connection.commit()
    connection.close()


# Initialize the database when the app starts
def initialize():
    init_db()


@app.before_request
def manage_session():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    if "username" in session:
        # Check if session has expired
        last_activity = session.get("last_activity")
        if last_activity:
            current_time = datetime.now()
            time_difference = current_time - last_activity.replace(tzinfo=None)
            if time_difference.total_seconds() > 1800:  # 30 minute
                session.clear()
                return redirect(url_for("login"))

    # Update the last activity timestamp for the session
    session["last_activity"] = datetime.now()


@app.context_processor
def inject_user():
    return {
        "authenticated": "username" in session,
        "admin": session.get("admin", False),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/BookingPage", methods=["GET", "POST"])
def BookingPage_page():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        course = request.form.get("courses")
        date = request.form.get("date")
        time = request.form.get("time")

        if not course or not date or not time:
            return "Please fill out all fields", 400

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Create bookings table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY,
                courses TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """
        )

        try:
            # Insert the booking
            cursor.execute(
                "INSERT INTO bookings (courses, date, time, username) VALUES (?, ?, ?, ?)",
                (course, date, time, session.get("username")),
            )
            connection.commit()
            connection.close()
            return redirect("/booking_confirm")
        except sqlite3.Error as e:
            connection.close()
            return f"Booking failed: {e}", 500

    # Fetch available courses from the database
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT course_name FROM courses"
    )  # Adjust table/column names as needed
    courses = cursor.fetchall()
    connection.close()

    # Pass courses to the template
    return render_template(
        "BookingPage.html", courses=[course[0] for course in courses]
    )


@app.route("/Orderingpage", methods=["GET", "POST"])
def Orderingpage_page():
    return render_template("Orderingpage.html")


@app.route("/Order", methods=["GET", "POST"])
def Order():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item = request.form.get("product")
        quantity = request.form.get("quantity")

        if not item or not quantity:
            return ("Please fill out all fields",)

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Create orders table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                item TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """
        )

        try:
            # Insert the order
            cursor.execute(
                "INSERT INTO orders (item, quantity, username) VALUES (?, ?, ?)",
                (item, quantity, session.get("username")),
            )
            connection.commit()
            connection.close()
            return redirect("/ordering_confirm")
        except sqlite3.Error:
            connection.close()
            return "Order failed", 500
    return render_template("Orderingpage.html")


@app.route("/test")
def test_page():
    return render_template("test.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/courses")
def get_courses():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT course_id, course_name, course_description FROM courses")
    courses = cursor.fetchall()
    conn.close()
    return render_template("courses_info.html", courses=courses)


@app.route("/confirm")
def confirm():
    return render_template("confirm.html")


@app.route("/booking_confirm")
def booking_confirm():
    return render_template("booking_confirm.html")


@app.route("/ordering_confirm")
def ordering_confirm():
    return render_template("ordering_confirm.html")


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    # Verify user exists in database
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Check if user exists in database
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        connection.close()
        session.pop("username", None)  # Clear invalid session
        return redirect(url_for("login"))

    # Fetch user-specific bookings
    cursor.execute("SELECT courses, date FROM bookings WHERE username = ?", (username,))
    bookings = cursor.fetchall()
    connection.close()

    return render_template("profile.html", username=username, bookings=bookings)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate input lengths
        if len(username) > 200 or len(password) > 200:
            return "Input exceeds character limit", 400

        # Check if the user exists in the database
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Modified query to include admin column
        cursor.execute(
            "SELECT username, password, admin FROM users WHERE username = ?",
            (username,),
        )
        user = cursor.fetchone()
        connection.close()

        if user:
            admin = user[2]  # Get admin status
            if admin:
                # For admin accounts, direct password comparison
                if password == user[1]:  # Direct comparison for admin passwords
                    session["username"] = username
                    session["admin"] = True
                    return redirect(url_for("profile"))
            else:
                # For regular users, check hashed password
                if check_password_hash(user[1], password):
                    session["username"] = username
                    session["admin"] = False
                    return redirect(url_for("profile"))

        return "Invalid username or password", 400

    return render_template("login.html")


@app.route("/Sign-Up", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return "Please fill out all fields", 400  # Simple error handling

        # Validate input lengths
        if len(username) > 15 or len(email) > 50 or len(password) > 20:
            return "Input exceeds character limit", 400
        if len(username) < 3 or len(email) < 3 or len(password) < 8:
            return "Input is below character limit", 400

        # Validate characters in username and email
        if (
            not re.match("^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", username)
            or not re.match("^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", email)
            or not re.match(
                "^[a-zA-Z0-9@._!;#$%&'()*+,-./:;<=>?@[\]^_`{|}~]+$", password
            )
        ):
            return "Invalid characters in username, email or password", 400
        # Validate password strength
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            password,
        ):
            return (
                "Password must contain at least 8 characters, including uppercase, lowercase, digits, and special characters.",
                400,
            )
        # Hash the password
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Insert user into database
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Check if the username or email already exists
        cursor.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?", (username, email)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            return "Username or email already exists.", 400

        try:
            # Insert the user
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_password),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            return "User already exists or email is already registered.", 400
        finally:
            connection.close()

        # Redirect to confirmation page
        return redirect("/confirm")

    return render_template("Sign-Up.html")


@app.route("/weather_page")
def health():
    return render_template("weather_page.html")





@app.route("/theme", methods=["POST"])
def set_theme():
    theme = request.form.get("theme")
    session["theme"] = theme
    return "", 204


@app.context_processor
def inject_theme():
    theme = session.get("theme", "light")
    return dict(theme=theme)


def inject_user():
    return {"is_authenticated": "username" in session}


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not all([current_password, new_password, confirm_password]):
            return ("Please fill out all fields",)

        if new_password != confirm_password:
            return "New passwords do not match", 400

        if len(new_password) < 8 or len(new_password) > 20:
            return "New password must be between 8 and 20 characters", 400

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username = ?", (session["username"],)
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(user[0], current_password):
            connection.close()
            return "Current password is incorrect", 400

        hashed_password = generate_password_hash(new_password, method="pbkdf2:sha256")
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed_password, session["username"]),
        )
        connection.commit()
        connection.close()

        return render_template("profile.html")

    return render_template("profile.html")


@app.route("/usersinfo")
def users_info():
    if "username" not in session or not session.get("admin"):
        return redirect(url_for("login"))

    try:
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, email, admin FROM users")
        users = cursor.fetchall()

        cursor.execute(
            "SELECT course_id, course_name, course_description, course_duration FROM courses"
        )
        courses = cursor.fetchall()

        connection.close()
        return render_template("users_info.html", users=users, courses=courses)
    except sqlite3.Error as e:
        return f"Database error: {str(e)}", 500


@app.route("/add_course", methods=["POST"])
def add_course():
    if "username" not in session or not session.get("admin"):
        return redirect(url_for("login"))

    course_name = request.form.get("course_name")
    course_description = request.form.get("course_description")
    course_duration = request.form.get("courses")

    if not course_name or not course_description or not course_duration:
        return "Please fill out all fields", 400

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Create courses table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_description TEXT NOT NULL,
            course_duration INTEGER NOT NULL
        )
    """
    )

    try:
        # Insert the new course
        cursor.execute(
            "INSERT INTO courses (course_name, course_description, course_duration) VALUES (?, ?, ?)",
            (course_name, course_description, course_duration),
        )
        connection.commit()
        connection.close()
        return redirect("/usersinfo")
    except sqlite3.Error as e:
        connection.close()
        return f"Failed to add course: {e}", 500  

@app.route("/delete_course", methods=["POST"])
def delete_course():
    if "username" not in session or not session.get("admin"):
        return redirect(url_for("login"))

    course_id = request.form.get("course_id")

    if not course_id:
        return "Please provide a course ID", 400

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        connection.commit()
        connection.close()
        return redirect("/usersinfo")
    except sqlite3.Error as e:
        connection.close()
        return f"Failed to delete course: {e}", 500
    
@app.route("/delete_user", methods=["POST"])
def delete_user():
    if "username" not in session or not session.get("admin"):
        return redirect(url_for("login"))

    user_id = request.form.get("user_id")

    if not user_id:
        return "Please provide a user ID", 400

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        connection.close()
        return redirect("/usersinfo")
    except sqlite3.Error as e:
        connection.close()
        return f"Failed to delete user: {e}", 500
    
@app.route("/set_cookie", methods=["POST"])
def set_cookie():
    response = make_response(redirect(url_for("index")))
    response.set_cookie("cookie_consent", "true", max_age=60 * 60 * 24 * 365)  # 1 year
    return response

@app.route("/search", methods=["GET"])
def search():
    if "username" not in session or not session.get("admin"):
        return redirect(url_for("login"))

    query = request.args.get("q", "").lower()
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Search users
    cursor.execute("SELECT id, username, email FROM users WHERE LOWER(username) LIKE ? OR LOWER(email) LIKE ?", 
                    (f"%{query}%", f"%{query}%"))
    users = cursor.fetchall()

    # Search courses 
    cursor.execute("SELECT course_id, course_name, course_description FROM courses WHERE LOWER(course_name) LIKE ? OR LOWER(course_description) LIKE ?",
                    (f"%{query}%", f"%{query}%"))
    courses = cursor.fetchall()

    connection.close()
    return jsonify({
        "users": users,
        "courses": courses
    })
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/weather_page")
def weather_page():
    return render_template("weather_page.html")


@app.route("/weather_data")
def get_weather_data():
    api_key = '0f98d01acd0e41818d8124023242111'
    url = f'https://api.weatherapi.com/v1/forecast.json?key={api_key}&q=horsham&days=4&aqi=no'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx, 5xx
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch weather data", "details": str(e)})



# Error handler for 404
@app.errorhandler(404)
def page_not_found(_):
    app.logger.error(f"Page not found: {request.url}")
    return render_template("404.html"), 404


if __name__ == "__main__":
    initialize()
    app.run(debug=True, host="0.0.0.0")