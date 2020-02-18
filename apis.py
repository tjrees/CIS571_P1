# user.py
from flask import *
from config import *
import os, hashlib, re, uuid, datetime, jwt
from external_apis import *

my_api = Blueprint('my_api', __name__, template_folder='templates')

protected_usernames = {
	'INVALID': 1,
	'EXPIRED': 1
}

# User information validation functions
def is_blank(field):
	if not field:
		return True
	else:
		return False

def too_long(field, max_length):
	return (len(field) > max_length)

def too_short(field, min_length):
	return (len(field) < min_length)

def duplicate_username(username):
	if username in protected_usernames:
		return True

	db = connect_to_database()
	cursor = db.cursor()
	query = 'SELECT * FROM Users WHERE username = %s'
	cursor.execute(query, (username,))
	results = cursor.fetchall()
	if not results:
		return False
	else:
		return True

def insecure_password(password):
	if (bool(re.search(r"\d", password))) and bool((re.search(r"[A-Za-z]", password))):
		return False
	else:
		return True

def invalid_email(email):
	if re.match(r"[^@]+@[^@]+\.[^@]+", email):
		return False
	else:
		return True

def validate_user_info(username, password, confirmpassword, name, email):
	errors = []

	if is_blank(username):
		errors.append({'message': 'username cannot be blank'})
	if is_blank(password):
		errors.append({'message': 'password cannot be blank'})
	if is_blank(confirmpassword):
		errors.append({'message': 'confirmpassword cannot be blank'})
	if is_blank(name):
		errors.append({'message': 'name cannot be blank'})
	if is_blank(email):
		errors.append({'message': 'email cannot be blank'})

	if too_long(username, 20):
		errors.append({'message': 'username must be 20 characters or fewer'})
	if too_long(password, 20):
		errors.append({'message': 'password must be 20 characters or fewer'})
	if too_long(name, 30):
		errors.append({'message': 'name must be 30 characters or fewer'})
	if too_long(email, 30):
		errors.append({'message': 'email must be 30 characters or fewer'})

	if too_short(username, 5):
		errors.append({'message': 'username must be at least 5 characters long'})
	if too_short(password, 8):
		errors.append({'message': 'password must be at least 8 characters long'})
	if too_short(name, 1):
		errors.append({'message': 'name must be at least 1 character long'})

	if insecure_password(password):
		errors.append({'message': 'password must contain a letter and a number'})

	if invalid_email(email):
		errors.append({'message': 'must provide a valid email address'})

	if duplicate_username(username):
		errors.append({'message': 'username is already taken'})

	if (confirmpassword != password):
		errors.append({'message': 'password and confirmpassword do not match'})

	return errors

def hash_password(password):
	salt = uuid.uuid4().hex
	hash_object = hashlib.new('sha512')
	hash_object.update(str(salt + password).encode('utf-8'))
	hash_str = hash_object.hexdigest()
	database_password = salt + '$' + hash_str
	return database_password

def encode_token(username):
	token_payload = {
		'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
		'iat': datetime.datetime.utcnow(),
		'sub': username
	}
	token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
	return token.hex()

def decode_token(hextoken):
	token = bytes.fromhex(hextoken)
	try:
		token_payload = jwt.decode(token, SECRET_KEY)
		return token_payload['sub']
	except jwt.ExpiredSignatureError:
		return 'EXPIRED'
	except jwt.InvalidTokenError:
		return 'INVALID'

def verify_login(username, password):
	db = connect_to_database()
	cursor = db.cursor()
	query = 'SELECT password FROM Users WHERE username = %s'
	cursor.execute(query, (username,))
	results = cursor.fetchone()
	if not results:
		return False

	database_password = results['password']

	split_password = database_password.split('$')
	salt = split_password[0]
	hashed_password = split_password[1]

	test_hash = hashlib.new('sha512')
	test_hash.update(str(salt + password).encode('utf-8'))
	test_hash_str = test_hash.hexdigest()
	return (test_hash_str == hashed_password)


# API routes
@my_api.route('/api/user', methods=['POST', 'DELETE'])
def api_register_user():
	if request.method == 'POST':
		request_data = request.get_json()
		if ('username' not in request_data or
			'password' not in request_data or
			'confirmpassword' not in request_data or
			'name' not in request_data or
			'email' not in request_data):

			errors = []
			errors.append({'message':'Request for a new user must contain username, password, confirmpassword, name, and email'})
			return jsonify(errors=errors), 400

		username = request_data['username']
		password = request_data['password']
		confirmpassword = request_data['confirmpassword']
		name = request_data['name']
		email = request_data['email']

		errors = validate_user_info(username, password, confirmpassword, name, email)
		if errors:
			return jsonify(errors=errors), 400

		database_password = hash_password(password)

		db = connect_to_database()
		cursor = db.cursor()
		query = 'INSERT INTO Users (username, password, name, email) VALUES (%s, %s, %s, %s)'
		cursor.execute(query, (username, database_password, name, email))
		return jsonify(result='New user successfully created'), 201

	else: # DELETE
		request_data = request.get_json()
		if ('username' not in request_data or
			'password' not in request_data):

			errors = []
			errors.append({'message':'Request to delete a user account requires username and password'})
			return jsonify(errors=errors), 400

		username = request_data['username']
		password = request_data['password']
		if verify_login(username, password):
			db = connect_to_database()
			cursor = db.cursor()
			query = 'DELETE FROM Users WHERE username = %s'
			cursor.execute(query, (username,))
			return jsonify(result='Account successfully deleted'), 200

		else:
			errors = []
			errors.append({'message': 'Delete user request failed; either username or password is incorrect'})
			return jsonify(errors=errors), 401


@my_api.route('/api/login', methods=['POST'])
def api_login_user():
	request_data = request.get_json()
	if ('username' not in request_data or
		'password' not in request_data):

		errors = []
		errors.append({'message':'Login request must contain a username and password'})
		return jsonify(errors=errors), 400

	username = request_data['username']
	password = request_data['password']

	# Give the user a token if the login is successful. Send an error message otherwise
	if verify_login(username, password):
		token = encode_token(username)
		return jsonify({'token':token}), 200

	else:
		errors = []
		errors.append({'message': 'Login failed; either username or password is incorrect'})
		return jsonify(errors=errors), 401

def get_saved_trails(token):

	decode_result = decode_token(token)

	if decode_result in protected_usernames:
		return decode_result

	username = decode_result # Valid token returns username
	db = connect_to_database()
	cursor = db.cursor()
	query = 'SELECT trail FROM Trails WHERE username = %s'
	cursor.execute(query, (username,))

	results = cursor.fetchall()
	if not results:
		return {'trails':[]}

	trail_ids = []
	for result in results:
		trail_ids.append(result['trail'])

	request_input = ','.join(trail_ids)
	trails = get_trails_by_id(request_input)
	return trails

@my_api.route('/api/trails', methods=['GET', 'POST', 'DELETE'])
def api_save_trails():
	if request.method == 'POST':
		request_data = request.get_json()
		if ('token' not in request_data or
			'trails' not in request_data):

			errors = []
			errors.append({'message':'Request to save trails must include the authentication token and a list of trails'})
			return jsonify(errors=errors), 400

		token = request_data['token']
		trails = request_data['trails']

		decode_result = decode_token(token)
		if decode_result in protected_usernames:
			errors = []
			errors.append({'message':'Your token is either expired or invalid. Please log in to get a token.'})
			return jsonify(errors=errors), 401

		username = decode_result # Valid token returns username

		db = connect_to_database()
		cursor = db.cursor()
		query = 'INSERT INTO Trails (trail, username) VALUES (%s, %s)'
		for trail_id in trails:
			try:
				cursor.execute(query, (trail_id, username))
			except:
				# Duplicate entries will not be created, but will not
				# throw an error
				pass

		return jsonify(result='Trails have been successfully saved'), 201

	elif request.method == 'GET': # GET
		request_data = request.get_json()
		if ('token' not in request_data):
			errors = []
			errors.append({'message':'Request to retrieve saved trails must include an authentication token'})
			return jsonify(errors=errors), 400

		token = request_data['token']

		trails = get_saved_trails(token)

		if (trails == 'EXPIRED' or
			trails == 'INVALID'):
			errors = []
			errors.append({'message','Your token is either expired or invalid. Please log in to get a token.'})
			return jsonify(errors=errors), 401

		return jsonify(result=trails), 200

	else: # DELETE
		request_data = request.get_json()
		if ('token' not in request_data):
			errors = []
			errors.append({'message':'Request to delete saved trails must include an authentication token'})
			return jsonify(errors=errors), 400

		token = request_data['token']
		trails = request_data['trails']

		decode_result = decode_token(token)
		if decode_result in protected_usernames:
			errors = []
			errors.append({'message':'Your token is either expired or invalid. Please log in to get a token.'})
			return jsonify(errors=errors), 401

		username = decode_result # Valid token returns username

		db = connect_to_database()
		cursor = db.cursor()
		query = 'DELETE FROM Trails WHERE trail = %s AND username = %s'
		for trail_id in trails:
			try:
				cursor.execute(query, (trail_id, username))
			except:
				pass

		return jsonify(result='Trails have been successfully deleted'), 201




