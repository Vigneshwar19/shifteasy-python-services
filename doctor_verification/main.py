import logging
import time
from flask import Flask, request, jsonify
from app.utils.doctor_verification import doctor_verification

app = Flask(__name__)

log_file = 'verification_service_logs.log'

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

@app.route('/verification', methods=['POST'])
def verification():
    start_time = time.time()

    data = request.json
    reg_no = data.get('reg_no')
    council = data.get('council')
    customerId = data.get('customerId')
    verificationFor = data.get('verificationFor')

    logger.info(f"Received verification request: {data}")

    if not reg_no:
        logger.error("Registration number (reg_no) is required")
        return jsonify({"error": "Registration number (reg_no) is required"}), 400
    if not council:
        logger.error("Council name is required")
        return jsonify({"error": "Council name is required"}), 400
    if not customerId:
        logger.error("customerId is required")
        return jsonify({"error": "customerId is required"}), 400
    if not verificationFor:
        logger.error("verificationFor is required")
        return jsonify({"error": "verificationFor is required"}), 400

    try:
        if verificationFor == "doctor":
            url = "https://www.nmc.org.in/information-desk/indian-medical-register/"
            logger.info(f"Verifying doctor with registration number: {reg_no}")
            logger.info(f"Verifying doctor with url: {url}")
            response = doctor_verification(url, reg_no, council, customerId)
            logger.info(f"Doctor verification successful for reg_no: {reg_no}")
            logger.info(f"Doctor verification response: {response}")
        else:
            logger.warning(f"Verification service for {verificationFor} is still in process.")
            response = jsonify({"message": f"Verification service for {verificationFor} is still in process."}), 200

        response_time = time.time() - start_time
        logger.info(f"Response time for the request: {response_time:.2f} seconds")
        logger.info(f"-" * 100)

        return response
        
    except Exception as e:
        logger.error(f"Error during verification: {str(e)}")
        logger.info(f"-" * 100)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8602, debug=True)
