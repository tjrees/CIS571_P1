# user.py
from flask import *
from config import *
import os, hashlib, re, uuid

user_api = Blueprint('user_api', __name__, template_folder='templates')

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

# API routes
@user_api.route('/api/user', methods=['POST'])
def api_register_user():
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
	cursor.execute(query, (username, password, name, email))
	return jsonify(result='New user successfully created'), 201
