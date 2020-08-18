'''
'''

# Import Modules:

import json
import uuid
from datetime import datetime
from threading import Thread
from flask import Flask
from flask import current_app as c_app
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from bindings.flask_mongo import FlaskMongo
from bson.objectid import ObjectId
from middleware.decorators import is_valid_args, is_valid_json
from utils.common_functions import format_api_error
from utils.send_emails import Gmailer
from app.schema import Email
from bindings.flask_logger import FlaskLogger

email_schema = Email()

# Class Definitions:

class EmailsCreator(Resource):
	'''
	'''
	def __init__(self):
		'''
		'''
		self.meta = {
			"version": 1.0,
			"timestamp": datetime.now().isoformat()
		}
		self.headers = {"Content-Type": "application/json"}
		self.success_code = 200
		self.processing_code = 202
		self.bad_code = 400
		self.no_data_code = 404
		self.process_error_code = 422
		self.exception_code = 500

	@is_valid_json
	def post(self):
		'''
		'''
		try:
			post_data = request.get_json()
			email_schema.load(post_data)

			receiver_email_id = post_data.get('receiver_email_id')
			email_message = post_data.get('email_message')

			mailer = Gmailer()
			background_task = Thread(
				target=mailer.send_mail, args=(receiver_email_id, email_message)
			)
			background_task.daemon = True
			background_task.start()

			response = {
				'meta': self.meta,
				'status': 'success',
				'message': f'sending email successfully'
			}
			return response, self.processing_code, self.headers

		except ValidationError as e:
			# raise e
			# print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"errors": format_api_error(e.messages)
			}
			FlaskLogger.log('post', 'create_email', response, input_data=str(post_data), log_level='error')
			return response, self.bad_code, self.headers

		except Exception as e:
			# raise e
			print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('post', 'create_email', response, input_data=str(post_data), log_level='warning')
			return response, self.exception_code, self.headers