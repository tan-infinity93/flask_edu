'''
'''

# Import Modules:

import json
import uuid
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from app.schema import Token
from middleware.decorators import is_valid_args, is_valid_json
from bindings.flask_mongo import FlaskMongo
from bindings.flask_logger import FlaskLogger
from utils.common_functions import generate_auth_token, format_api_error #get_uuid1, write_b64_to_file, save_file_to_s3

token_data = Token()

# Class Definitions:

class Auth(Resource):
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
		self.bad_code = 400
		self.auth_code = 401
		self.process_error_code = 422
		self.exception_code = 500

	@is_valid_json
	def post(self):
		'''
		'''
		try:
			post_data = request.get_json()
			token_data.load(post_data)

			columns = {"_id": 1, "account_type": 1}
			queries = post_data
			collection = 'common_user_master'
			user_data = FlaskMongo.find(collection, columns, queries)

			print(post_data)
			username = post_data.get('username')

			if user_data == []:
				response = {
					"meta": self.meta,
					# "message": f"user {username} does not exists",
					"message": "please check provided credentials",
					"status": "failure",
				}
				FlaskLogger.log('post', 'token_generation', response, log_level='info')
				return response, self.auth_code, self.headers

			user_data = user_data[0]
			auth_token = generate_auth_token(post_data, user_data)

			response = {
				"meta": self.meta,
				"token": auth_token,
				"status": "success"
			}
			FlaskLogger.log('post', 'token_generation', response, log_level='info')
			return response, self.success_code, self.headers

		except ValidationError as e:
			# raise e
			# print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"errors": format_api_error(e.messages)
			}
			FlaskLogger.log('post', 'token_generation', response, log_level='error')
			return response, self.bad_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('post', 'token_generation', response, log_level='warning')
			return response, self.exception_code, self.headers