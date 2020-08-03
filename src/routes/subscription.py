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
from app.schema import ResetTrial
from middleware.decorators import is_valid_args, is_valid_json
from bindings.flask_mongo import FlaskMongo
from utils.common_functions import format_api_error#get_uuid1, write_b64_to_file, save_file_to_s3

reset_trial_data = ResetTrial()

# Class Definitions:

class ResetTrial(Resource):
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
		self.process_error_code = 422
		self.exception_code = 500

	@is_valid_json
	def post(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			reset_trial_data.load(post_data)

			user_id = post_data.get("userid")
			collection = "common_user_master"
			queries = {"_id": ObjectId(user_id)}
			columns = {"_id": 0}

			user_data = FlaskMongo.find(collection, columns, queries)

			if not user_data:
				response = {
					"meta": self.meta,
					"message": f"user with id {user_id} does not exists",
					"status": "failure"
				}
				return response, self.bad_code, self.headers
			else:
				if args_data:
					no_free_trial = args_data.get('no_free_trial')
				else:
					no_free_trial = 2
				
				updates = {
					"no_free_trial": no_free_trial
				}
				FlaskMongo.update(collection, updates, queries)

				response = {
					"meta": self.meta,
					"message": f"trial for user with id {user_id} has been reset",
					"status": "success"
				}
				return response, self.success_code, self.headers

		except ValidationError as e:
			print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
			}
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
			return response, self.exception_code, self.headers
