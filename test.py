# Import necessary modules
import sqlite3  # For SQLite database management
from flask import (Flask,redirect,render_template,request,session,url_for,)  # For web development with Flask
from werkzeug.security import generate_password_hash, check_password_hash  # For password security
import re  # For input validation using regular expressions

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Secret key for securing sessions

# Initializes the database and ensure the users table exists
def init_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    # Create users table if it doesn't already exist
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
    connection.commit()  # Save changes
    connection.close()  # Close the connection


# Call database initialization when the app starts
def initialize():
    init_db()


# Context processor to make session data available to templates
@app.context_processor
def inject_user():
    # Pass a flag indicating if a user is logged in
    return dict(logged_in=("username" in session))


# Route for the home page
@app.route("/")
def index():
    # Render the index.html template
    return render_template("index.html"), 404  # Return 404 for demonstration


# Route for the booking page
@app.route("/BookingPage", methods=["GET", "POST"])
def BookingPage_page():
    # Redirect to login page if user is not logged in
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Get course and date from form input
        course = request.form.get("courses")
        date = request.form.get("date")

        # Validate that both fields are filled
        if not course or not date:
            return "Please fill out all fields", 400

        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()

        # Create bookings table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY,
                course TEXT NOT NULL,
                date TEXT NOT NULL,
                username TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """
        )

        try:
            # Insert new booking into the bookings table
            cursor.execute(
                "INSERT INTO bookings (course, date, username) VALUES (?, ?, ?)",
                (course, date, session.get("username")),
            )
            connection.commit()  # Save changes
            connection.close()  # Close the connection
            return redirect("/booking_confirm")
        except sqlite3.Error:
            connection.close()
            return "Booking failed", 400  # Error message if booking fails

    # Render the booking page template
    return render_template("BookingPage.html")


# Route for the ordering page
@app.route("/Orderingpage", methods=["GET", "POST"])
def Orderingpage_page():
    # Render the ordering page template
    return render_template("Orderingpage.html"), 404  # Return 404 for demonstration


# Route to handle order submission
@app.route("/Order", methods=["GET", "POST"])
def Order():
    # Redirect to login page if user is not logged in
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Get item and quantity from form input
        item = request.form.get("product")
        quantity = request.form.get("quantity")

        # Validate that both fields are filled
        if not item or not quantity:
            return "Please fill out all fields", 400

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
            # Insert new order into the orders table
            cursor.execute(
                "INSERT INTO orders (item, quantity, username) VALUES (?, ?, ?)",
                (item, quantity, session.get("username")),
            )
            connection.commit()  # Save changes
            connection.close()  # Close the connection
            return redirect("/ordering_confirm")
        except sqlite3.Error:
            connection.close()
            return "Order failed", 400  # Error message if order fails

    # Render the ordering page template
    return render_template("/Orderingpage")


# Test page route
@app.route("/test")
def test_page():
    # Render the test page template
    return render_template("test.html"), 404


# Route for the about page
@app.route("/about")
def about_page():
    # Render the about page template
    return render_template("about.html"), 404


# Route to fetch course details
@app.route("/courses")
def get_courses():
    # Fetch course details from the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT course_id, course_name, course_description FROM courses")
    courses = cursor.fetchall()
    conn.close()
    # Render the courses_info.html template with fetched data
    return render_template("courses_info.html", courses=courses)


# Route for booking confirmation
@app.route("/booking_confirm")
def booking_confirm():
    # Render the booking confirmation page template
    return render_template("booking_confirm.html")


# Route for ordering confirmation
@app.route("/ordering_confirm")
def ordering_confirm():
    # Render the ordering confirmation page template
    return render_template("ordering_confirm.html")


# Route for user profile
@app.route("/profile")
def profile():
    # Redirect to login page if user is not logged in
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    # Connect to the database
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    # Check if the user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        # If user does not exist, clear invalid session and redirect to login
        connection.close()
        session.pop("username", None)
        return redirect(url_for("login"))

    # Fetch user-specific bookings
    cursor.execute("SELECT course, date FROM bookings WHERE username = ?", (username,))
    bookings = cursor.fetchall()
    connection.close()

    # Render the profile.html template with user data
    return render_template("profile.html", username=username, bookings=bookings)


# Logout route to clear the session
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for("login"))


# Add more routes as needed, maintaining the same style.
# Additional routes like /login, /Sign-Up, and /change_password can be expanded similarly.

if __name__ == "__main__":
    initialize()
    app.run(debug=True)
