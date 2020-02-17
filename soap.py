# soap.py
from flask import *
from external_apis import *
import xml.etree.ElementTree as ET

soap_api = Blueprint('soap_api', __name__, template_folder='templates')


SOAP_NAMESPACES = {'soap': 'http://schemas.xmlsoap.org/soap/envelope'}
DIFFICULTY_MAP = {
	'green': 1,
	'greenBlue': 2,
	'blue': 3,
	'blueBlack': 4,
	'black': 5,
	'dblack': 6
}

# Returns an empty SOAP XML document with a tag for the input function_name
def create_soap_doc(function_name):
	soap_envelope = ET.Element('soap:Envelope')
	soap_envelope.attrib['xmlns:soap'] = 'http://schemas.xmlsoap.org/soap/envelope'
	soap_body = ET.SubElement(soap_envelope, 'soap:Body')
	soap_function = ET.SubElement(soap_body, function_name)
	return soap_envelope

# Returns the element containing the function data
def get_soap_function_data(soap_doc):
	soap_envelope = ET.fromstring(soap_doc)
	soap_body = soap_envelope.find('soap:Body', SOAP_NAMESPACES)
	function_data = soap_body.find('*')

	return function_data

def get_soap_error_doc(error_message):
	soap_envelope = create_soap_doc('Error')
	soap_body = soap_envelope.find('soap:Body')
	error_data = soap_body.find('*')
	error_data.text = error_message

	return ET.tostring(soap_envelope)

def soap_function_get_trip_gear(soap_function_data):
	overall_info = []
	trails = []

	trails_tag = soap_function_data.find('Trails')
	for trail_id in trails_tag.findall('Trail_ID'):
		trails.append(trail_id.text)

	if not trails:
		return '', False, 'Request submitted with no trails.'

	trails_joined = ','.join(trails)
	hikingproject_results = get_trails_by_id(trails_joined)
	trails_info = hikingproject_results['trails']

	# Collect useful info from the hiking project and weather unlocked APIs
	for info in trails_info:
		useful_info = {}

		# Hiking Project
		latitude = info['latitude']
		longitude = info['longitude']
		useful_info['length'] = info['length']
		#useful_info['highAltitude'] = info['high']
		useful_info['name'] = info['name']
		useful_info['difficulty'] = info['difficulty']

		# Weather Unlocked
		forecast_weather = get_forecast_weather(latitude, longitude)

		useful_info['temp_max_f'] = []
		useful_info['temp_min_f'] = []
		useful_info['rain_total_in'] = []
		#useful_info['snow_total_in'] = []
		useful_info['windspd_max_mph'] = []

		for day in forecast_weather['Days']:
			useful_info['temp_max_f'].append(day['temp_max_f'])
			useful_info['temp_min_f'].append(day['temp_min_f'])
			useful_info['rain_total_in'].append(day['rain_total_in'])
			#useful_info['snow_total_in'].append(day['snow_total_in'])
			useful_info['windspd_max_mph'].append(day['windspd_max_mph'])

		overall_info.append(useful_info)

	# Find 
	max_length = overall_info[0]['length']
	max_length_trail = overall_info[0]['name']
	max_difficulty = overall_info[0]['difficulty']
	max_difficulty_trail = overall_info[0]['name']

	max_temperature = overall_info[0]['temp_max_f'][0]
	max_temperature_trail = overall_info[0]['name']
	min_temperature = overall_info[0]['temp_min_f'][0]
	min_temperature_trail = overall_info[0]['name']
	max_rain_total = overall_info[0]['rain_total_in'][0]
	max_rain_total_trail = overall_info[0]['name']
	max_windspd = overall_info[0]['windspd_max_mph'][0]
	max_windspd_trail = overall_info[0]['name']


	for entry in overall_info:
		if entry['length'] > max_length:
			max_length = entry['length']
			max_length_trail = entry['name']

		if DIFFICULTY_MAP[entry['difficulty']] > DIFFICULTY_MAP[max_difficulty]:
			max_difficulty = entry['difficulty']
			max_difficulty_trail = entry['name']

		if max(entry['temp_max_f']) > max_temperature:
			max_temperature = max(entry['temp_max_f'])
			max_temperature_trail = entry['name']

		if min(entry['temp_min_f']) < min_temperature:
			min_temperature = min(entry['temp_min_f'])
			min_temperature_trail = entry['name']

		if max(entry['rain_total_in']) > max_rain_total:
			max_rain_total = max(entry['rain_total_in'])
			max_rain_total_trail = entry['name']

		if max(entry['windspd_max_mph']) > max_windspd:
			max_windspd = max(entry['windspd_max_mph'])
			max_windspd_trail = entry['name']

	# Determine gear based on the attributes of the planned trip
	gear_list = []

	# Basics
	gear_list.append({'item':'T-Shirt', 'info':'A t-shirt is a great base layer no matter the hike or weather conditions.'})
	gear_list.append({'item':'Water Bottle', 'info':'It is important to stay hydrated, no matter what hike you are doing.'})
	gear_list.append({'item':'First Aid Kit', 'info':'A first aid kit is important on any hike.'})

	# Food for a trail over 5 miles
	if (max_length >= 5.0):
		gear_list.append({'item':'Food', 'info':'It may be helpful to bring snacks on hikes of 5 or more miles.'})

	# Overnight gear for trails over 12 miles
	if (max_length >= 12.0):
		snippet = '%s is %f miles long. You may want to consider camping. A tent will help shelter you overnight.' % (max_length_trail, max_length)
		gear_list.append({'item':'Tent', 'info':snippet})
		snippet = '%s is %f miles long. You may want to consider camping. A sleeping bag will be great overnight.' % (max_length_trail, max_length)
		gear_list.append({'item':'Sleeping Bag', 'info':snippet})

	# If length is over 5 or difficulty is medium-hard to very hard, choose hiking boots over athletic shoes
	if (max_length >= 5.0 or max_difficulty in {'blueBlack', 'black', 'dblack'}):
		gear_list.append({'item':'Hiking Boots', 'info':'You have a hike at least 5 miles long, or one more difficult than blue. You will need the traction and support.'})
	else:
		gear_list.append({'item':'Athletic Shoes', 'info':'Your hikes are not too long or too difficult. The support provided by athletic shoes should be enough.'})
	
	# If temperature is over 55, bring shorts, sunglasses, and sunscreen
	if (max_temperature >= 55.0):
		snippet = '%s has a forecast high temperature of %f degrees Fahrenheit. Shorts will be a good idea to help keep cool.' % (max_temperature_trail, max_temperature)
		gear_list.append({'item':'Shorts', 'info':snippet})
		snippet = '%s has a forecast high temperature of %f degrees Fahrenheit, and could be sunny. Sunglasses will protect your eyes from UV rays.' % (max_temperature_trail, max_temperature)
		gear_list.append({'item':'Sunglasses', 'info':snippet})
		snippet = '%s has a forecast high temperature of %f degrees Fahrenheit, and could be sunny. Sunscreen will protect your skin from UV rays.' % (max_temperature_trail, max_temperature)
		gear_list.append({'item':'Sunscreen', 'info':snippet})

	# If temperature is over 70, bring a hiking hat. If it is under 70 but over 55, bring a baseball cap.
	if (max_temperature >= 70.0):
		snippet = '%s has a forecast high temperature of %f degrees Fahrenheit, and could be very sunny. A hiking hat will help shield your face and neck from the sun.' % (max_temperature_trail, max_temperature)
		gear_list.append({'item':'Hiking Hat', 'info':snippet})
	elif (max_temperature >= 55.0):
		snippet = '%s has a forecast high temperature of %f degrees Fahrenheit, and could be sunny. A baseball cap will help shield your face from the sun.' % (max_temperature_trail, max_temperature)
		gear_list.append({'item':'Baseball Cap', 'info':snippet})

	# If temperature is under 55, bring hiking pants.
	if (min_temperature < 55.0):
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. Hiking pants will provide some extra layering to keep you warm.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Hiking Pants', 'info':snippet})
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. A long-sleeve shirt will provide some extra layering to keep you warm.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Long-sleeve shirt', 'info':snippet})

	# If temperature is under 30, bring long underwear
	if (min_temperature < 30.0):
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. Long underwear will help keep you warm in sub-freezing temperatures.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Long Underwear', 'info':snippet})

	# If temperature is under 15, bring a heavy jacket
	if (min_temperature < 15.0):
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. A heavy winter jacket will help keep your body warm in frigid temperatures.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Heavy Winter Jacket', 'info':snippet})

	# If temperature is under 40, bring a knit hat, gloves, and a sweatshirt or light jacket
	if (min_temperature < 40.0):
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. A knit hat will help keep your ears and head warm.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Knit Hat', 'info':snippet})
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. Gloves will help keep your hands warm.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Warm gloves', 'info':snippet})
		snippet = '%s has a forecast low temperature of %f degrees Fahrenheit. A sweatshirt or light jacket will be enough to keep your body warm.' % (min_temperature_trail, min_temperature)
		gear_list.append({'item':'Sweatshirt or Light Jacket', 'info':snippet})

	# If the max wind speed is over 20 mph, bring a windbreaker
	if (max_windspd >= 20.0):
		snippet = '%s has forecast wind speeds of %f miles per hour. A windbreaker should help with your hike.' % (max_windspd_trail, max_windspd)
		gear_list.append({'item':'Windbreaker', 'info':snippet})

	# IF any trail is expecting a non-trivial amount of rain, bring a rain jacket.
	if (max_windspd > 0.1):
		snippet = '%s is expecting some rain. A rain jacket will help keep you dry.' % (max_rain_total_trail)
		gear_list.append({'item':'Rain Jacket', 'info':snippet})

	# Bring wool socks if you have any trails over 3 miles, any trails medium - very hard, or any temperatures below 40 degrees
	if (max_length >= 3.0 or max_difficulty in {'blue', 'blueBlack', 'black', 'dblack'} or min_temperature < 40):
		snippet = 'Wool socks are great for keeping your feet warm, wicking away moisture, and protecting your heels from blisters. They are a great addition to your gear set given your choices.'
		gear_list.append({'item':'Wool Socks', 'info':snippet})
	else:
		snippet = 'Athletic socks will be great for relatively short or easy hikes in reasonable temperatures.'
		gear_list.append({'item':'Athletic Socks', 'info':snippet})

	soap_envelope = create_soap_doc('getTripGearResponse')
	soap_body = soap_envelope.find('soap:Body')
	soap_response_data = soap_body.find('*')

	gear_tag = ET.SubElement(soap_response_data, 'Gear')

	for gear_item in gear_list:
		item_tag = ET.SubElement(gear_tag, 'Item')
		name_tag = ET.SubElement(item_tag, 'Name')
		name_tag.text = gear_item['item']
		info_tag = ET.SubElement(item_tag, 'Info')
		info_tag.text = gear_item['info']


	return ET.tostring(soap_envelope), True, ''
	

@soap_api.route('/soap/servlet/messagerouter', methods=['POST'])
def soap_handler():
	xml_string = request.get_data()

	try:
		soap_function_data = get_soap_function_data(xml_string)
		soap_function_name = soap_function_data.tag

		if (soap_function_name == 'getTripGear'):
			xml_return, success, error_message = soap_function_get_trip_gear(soap_function_data)
			if (success):
				return xml_return, 200
			else:
				return get_soap_error_doc(error_message), 400

		else:
			return get_soap_error_doc('Function name not recognized'), 400

	except:
		return get_soap_error_doc('Your input was formatted incorrectly'), 400

	return 'Hello World!'


