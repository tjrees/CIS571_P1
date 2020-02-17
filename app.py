from flask import Flask, render_template, redirect, url_for, request
from external_apis import *
from apis import *
from soap import *
import config


app = Flask(__name__)
app.register_blueprint(my_api)
app.register_blueprint(soap_api)

@app.route('/', methods=['GET'])
def index():
	return redirect(url_for('search_screen'))

@app.route('/login', methods=['GET'])
def login_screen():
	return render_template('login.html')

@app.route('/search', methods=['GET'])
def search_screen():
	return render_template('trail_search.html')

@app.route('/search/results', methods=['GET'])
def search_results_screen():
	latitude = request.args.get('latitude')
	longitude = request.args.get('longitude')
	maxDistance = request.args.get('maxDistance')
	minLength = request.args.get('minLength')

	if (not latitude or not longitude):
		return redirect(url_for('search_screen'))

	results = get_hiking_routes(latitude, longitude, maxDistance, minLength)

	options = {
		'trail_list': results['trails']
	}

	return render_template('search_results.html', **options)


@app.route('/plan', methods=['GET'])
def plan_screen():
	return render_template('plan_trip.html')


@app.route('/plan/saved', methods=['GET'])
def plan_saved_screen():
	token = request.args.get('token')

	if not token:
		return redirect(url_for('plan_screen'))

	results = get_saved_trails(token)

	options = {
		'trail_list': results['trails']
	}
	return render_template('plan_saved.html', **options)

@app.route('/signup', methods=['GET'])
def signup_screen():
	return render_template('signup.html')


if __name__ == '__main__':
    app.run(host=config.env['host'], port=config.env['port'], debug=True)
