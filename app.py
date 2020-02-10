from flask import Flask, render_template, redirect, url_for
from external_apis import external_apis
from user import user_api
import config


app = Flask(__name__)
app.register_blueprint(external_apis)
app.register_blueprint(user_api)

@app.route('/')
def index():
	return redirect(url_for('search_screen'))

@app.route('/login')
def login_screen():
	return render_template('login.html')

@app.route('/search')
def search_screen():
	return render_template('trail_search.html')

@app.route('/signup')
def signup_screen():
	return render_template('signup.html')


if __name__ == '__main__':
    app.run(host=config.env['host'], port=config.env['port'], debug=True)