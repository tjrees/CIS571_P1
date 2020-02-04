# external_apis.py
from flask import jsonify, Blueprint, request
from config import *
import requests

external_apis = Blueprint('external_apis', __name__,
							template_folder='templates')

@external_apis.route('/api/hikingroutes')
def get_hiking_routes():

	latitude = request.args.get('latitude')
	longitude = request.args.get('longitude')

	request_params = {}
	request_params['key'] = HIKING_PROJECT_KEY
	request_params['lat'] = latitude
	request_params['lon'] = longitude

	request_obj = requests.get(url = HIKING_PROJECT_ENDPOINT, params = request_params)

	trail_list = request_obj.json()

	if (trail_list['success'] == 1):
		i = 0
		for trail in trail_list['trails']:
			i += 1
			print (i, '. ', trail['name'], ' - ', trail['summary'], '\n')

	return jsonify(message='hello world!')