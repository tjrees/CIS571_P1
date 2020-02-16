# external_apis.py
from flask import jsonify, Blueprint, request
from config import *
import requests
import json

def get_hiking_routes(latitude, longitude):
	request_params = {}
	request_params['key'] = HIKING_PROJECT_KEY
	request_params['lat'] = latitude
	request_params['lon'] = longitude

	request_obj = requests.get(url = HIKING_PROJECT_ENDPOINT + 'get-trails', params = request_params)

	trail_list = request_obj.json()
	return trail_list

def get_trails_by_id(trails):
	request_params = {}
	request_params['key'] = HIKING_PROJECT_KEY
	request_params['ids'] = trails;

	request_obj = requests.get(url = HIKING_PROJECT_ENDPOINT + 'get-trails-by-id', params = request_params)

	trail_list = request_obj.json()
	return trail_list


def send_weather_request(final_url):
	request_params = {}
	request_params['app_id'] = WEATHER_UNLOCKED_APP_ID
	request_params['app_key'] = WEATHER_UNLOCKED_KEY

	headers = {'Accept' : 'application/json'}

	request_obj = requests.get(url = final_url, params = request_params, headers = headers)

	current_weather = request_obj.json()

	if (request_obj.status_code == requests.codes.ok):
		return current_weather
	else:
		return 'Weather details not available'

def get_current_weather(latitude, longitude):
	final_url = WEATHER_UNLOCKED_ENDPOINT + 'current/' + str(latitude) + ',' +  str(longitude)
	return send_weather_request(final_url)


def get_forecast_weather(latitude, longitude):
	final_url = WEATHER_UNLOCKED_ENDPOINT + 'forecast/' + str(latitude) + ',' +  str(longitude)
	return send_weather_request(final_url)
