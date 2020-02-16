# config.py
import pymysql
import os

HIKING_PROJECT_ENDPOINT = 'https://www.hikingproject.com/data/'
HIKING_PROJECT_KEY = '200676781-66089f3dc6eb42f0fb597c627c282471'

WEATHER_UNLOCKED_ENDPOINT = 'http://api.weatherunlocked.com/api/'
WEATHER_UNLOCKED_APP_ID = '3351ed58'
WEATHER_UNLOCKED_KEY = '7fd03bf9d5bdba67580b25aec4f38088'

SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret')

env = dict(
	host = '0.0.0.0',
	port = 5000,
	user = 'root', 
	passwd = 'root571GB',
	db = 'CIS571_P1',
)

def connect_to_database():
	options = {
		'host': env['host'],
		'user': env['user'],
		'passwd': env['passwd'],
		'db': env['db'],
		'cursorclass' : pymysql.cursors.DictCursor
	}
	db = pymysql.connect(**options)
	db.autocommit(True)
	return db