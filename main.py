from flask import Flask, render_template

app = Flask(__name__)
# hello world
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def about():
    return render_template('test.html')
app.run(debug=True)