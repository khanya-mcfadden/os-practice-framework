from flask import Flask, render_template, request

app = Flask(__name__)

# hello world
@app.route('/')
def index():
    return render_template('index.html'),404

@app.route('/test')
def test_page():
    return render_template('test.html'),404

@app.route('/about')
def about_page():
    return render_template('about.html'),404

@app.route('/courses')
def courses_page():
    return render_template('courses.html'),404


@app.route('/login')
def login_page():
    return render_template('login.html'),404

# Error handler for 404
@app.errorhandler(404)
def page_not_found(_):
    app.logger.error(f"Page not found: {request.url}")
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
