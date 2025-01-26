from flask import Flask, request
from flask_restful import Resource, Api
from twocaptcha import TwoCaptcha
import base64
import io
from PIL import Image
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
load_dotenv()

solver = TwoCaptcha(os.getenv("API_KEY"))
app = Flask(__name__)
api = Api(app)

last_solved_captcha_id = None

class SolveCaptcha(Resource):
    def post(self):
        global last_solved_captcha_id
        logging.info("Received a POST request for solving captcha.")
        try:
            base64_image = request.json['base64']
            logging.info("Received base64 image, decoding...")
            
            image_data = io.BytesIO(base64.b64decode(base64_image))
            img = Image.open(image_data)
            img.save('temp_captcha.png')
            logging.info("Saved the decoded image as temp_captcha.png.")

            logging.info("Attempting to solve the captcha...")
            result = solver.normal(file='temp_captcha.png')

            logging.debug("Solver result: %s", result)
            
            last_solved_captcha_id = result.get('captchaId', '')
            captcha_text = result.get('code', '')
            
            if not last_solved_captcha_id or not captcha_text:
                logging.warning("Captcha solving did not return valid ID or text.")
            
            logging.info("Captcha solved, with the captcha ID: %s", last_solved_captcha_id)
            return {"captcha_text": captcha_text, "captchaID": last_solved_captcha_id}
            
        except Exception as e:
            logging.error("An error occurred: %s", str(e))
            return {"error": str(e)}
        finally:
            if os.path.exists('temp_captcha.png'):
                os.remove('temp_captcha.png')
                logging.info("Temp captcha image removed.")

class ReportIncorrect(Resource):
    def post(self):
        global last_solved_captcha_id
        logging.info("Received a POST request for reporting incorrect captcha.")
        
        if last_solved_captcha_id:
            try:
                logging.info("Attempting to report the captcha...")
                solver.report(last_solved_captcha_id, False)
                logging.info("Captcha reported successfully.")
                
                return {"status": "reported"}
            except Exception as e:
                logging.error("An error occurred: %s", str(e))
                return {"error": str(e)}
        else:
            logging.info("No recent captcha to report...")
            return {"status": "no last captcha"}

api.add_resource(SolveCaptcha, '/solve')
api.add_resource(ReportIncorrect, '/report')

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(debug=True, port=5000)
