# external_apis.py
from flask import jsonify, Blueprint, request
from config import *
import requests
import json

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
		return json.dumps(trail_list['trails'])
	else:
		return json.dumps(trail_list['message'])


@external_apis.route('/api/currentweather')
def get_current_weather():
	latitude = request.args.get('latitude')
	longitude = request.args.get('longitude')

	final_url = WEATHER_UNLOCKED_ENDPOINT + 'current/' + str(latitude) + ',' +  str(longitude)

	request_params = {}
	request_params['app_id'] = WEATHER_UNLOCKED_APP_ID
	request_params['app_key'] = WEATHER_UNLOCKED_KEY

	headers = {'Accept' : 'application/json'}

	request_obj = requests.get(url = final_url, params = request_params, headers = headers)

	print(request_obj)

	current_weather = request_obj.json()

	if (request_obj.status_code == requests.codes.ok):
		return json.dumps(current_weather)
	else:
		return 'Weather details not available'

@external_apis.route('/api/forecastweather')
def get_forecast_weather():
	latitude = request.args.get('latitude')
	longitude = request.args.get('longitude')

	final_url = WEATHER_UNLOCKED_ENDPOINT + 'forecast/' + str(latitude) + ',' +  str(longitude)

	request_params = {}
	request_params['app_id'] = WEATHER_UNLOCKED_APP_ID
	request_params['app_key'] = WEATHER_UNLOCKED_KEY

	headers = {'Accept' : 'application/json'}

	request_obj = requests.get(url = final_url, params = request_params, headers = headers)

	print(request_obj)

	forecast_weather = request_obj.json()

	if (request_obj.status_code == requests.codes.ok):
		return json.dumps(forecast_weather)
	else:
		return 'Weather details not available'
