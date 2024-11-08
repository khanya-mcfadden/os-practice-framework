from flask import Flask, render_template

app = Flask(__name__)

# hello world
@app.route('/')
def index():
    return render_template('home.html')

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

if __name__ == "__main__":
    app.run(debug=True)
