import logging
import time
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.fetch_countries import fetch_countries
from utils.fetch_states import fetch_states
from utils.fetch_districts import fetch_districts
from utils.fetch_area import fetch_area

app = Flask(__name__)
front_end_urls = os.getenv('FRONT_END_URLS', '').split(',')
CORS(app, origins=front_end_urls)

log_file = 'fetch_location_logs.log'

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

@app.route('/fetch-all-countries', methods=['GET'])
def fetch_all_countries():
    start_time = time.time()

    logger.info(f"Request came to fetch all countries.")

    try:
        response = fetch_countries()
        logger.info(f"response: {response}")

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500
    
@app.route('/fetch-all-states', methods=['GET'])
def fetch_all_states():
    start_time = time.time()

    country = request.args.get('country')

    if not country:
        return jsonify({"warning": "Country parameter is required"}), 400

    logger.info(f"Request came to fetch all states from {country}.")

    try:
        response = fetch_states(country)
        logger.info(f"response: {response}")

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500
    
@app.route('/fetch-all-districts', methods=['GET'])
def fetch_all_districts():
    start_time = time.time()

    state = request.args.get('state')
    country = request.args.get('country')

    if not country:
        return jsonify({"warning": "Country parameter is required"}), 400

    if not state:
        return jsonify({"warning": "State parameter is required"}), 400

    logger.info(f"Request came to fetch all districts from {state}, {country}.")

    try:
        response = fetch_districts(state, country)
        logger.info(f"response: {response}")

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500
    
@app.route('/fetch-area', methods=['POST'])
def fetch():
    start_time = time.time()

    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    logger.info(f"Received request: {data}")

    if not latitude:
        logger.error("latitude (latitude) is required")
        return jsonify({"error": "latitude (latitude) is required"}), 400
    if not longitude:
        logger.error("longitude is required")
        return jsonify({"error": "longitude is required"}), 400

    try:
        response = fetch_area(latitude, longitude)
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
    app.run(host='0.0.0.0', port=8604, debug=True)
