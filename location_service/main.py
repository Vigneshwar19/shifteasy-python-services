import logging
import time
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.geocode_request import handle_geocode_request
from app.geonames.countries import get_all_countries
from app.geonames.states import fetch_and_save_all_states
from app.geonames.districts import fetch_and_save_all_districts
from app.geonames.nearby import fetch_and_save_all_nearby
from app.geonames.areas import fetch_and_save_all_areas
from app.geoname import *
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
front_end_urls = os.getenv('FRONT_END_URLS', '').split(',')
CORS(app, origins=front_end_urls)

log_file = 'location_service_logs.log'

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler(log_file)
    ]
)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
    
@app.route('/all-countries', methods=['GET'])
def all_countries():
    start_time = time.time()

    try:
        response = get_all_countries()

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500
    
@app.route('/all-states', methods=['GET'])
def states():
    start_time = time.time()

    try:
        response = fetch_and_save_all_states()

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500

@app.route('/all-districts', methods=['GET'])
def districts():
    start_time = time.time()

    try:
        response = fetch_and_save_all_districts()

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500

@app.route('/all-nearby', methods=['GET'])
def nearby():
    start_time = time.time()

    try:
        response = fetch_and_save_all_nearby()

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500
    
@app.route('/all-areas', methods=['GET'])
def areas():
    start_time = time.time()

    try:
        response = fetch_and_save_all_areas()

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500

@app.route('/find-address', methods=['POST'])
def find_address():
    start_time = time.time()

    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    try:
        customerId = int(data.get('customerId') or 0)
    except ValueError:
        customerId = 0

    logger.info(f"Received request: {data}")

    if not latitude:
        logger.error("latitude (latitude) is required")
        return jsonify({"error": "latitude (latitude) is required"}), 400
    if not longitude:
        logger.error("longitude is required")
        return jsonify({"error": "longitude is required"}), 400

    try:
        response = handle_geocode_request(latitude, longitude, customerId)
        logger.info(f"response: {response}")

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8603, debug=False)
