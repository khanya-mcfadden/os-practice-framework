from flask import Flask, render_template, request

app = Flask(__name__)

# hello world
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-page')
def test_page():
    return render_template('test.html')

@app.route('/about-page')
def about_page():
    return render_template('about.html')

@app.route('/courses-page')
def courses_page():
    return render_template('courses.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

# Error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    app.logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(f"Server error: {request.url}")
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    app.logger.error(f"Forbidden: {request.url}")
    return render_template('403.html'), 403

@app.errorhandler(400)
def bad_request(error):
    app.logger.error(f"Bad request: {request.url}")
    return render_template('400.html'), 400

if __name__ == "__main__":
    app.run(debug=True)
