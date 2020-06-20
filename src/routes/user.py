'''
'''

# Import Modules:

import json
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from app.schema import Users
from bindings.flask_mongo import FlaskMongo
# from utils.common_functions import get_uuid1, write_b64_to_file, save_file_to_s3

users_data = Users()

# Class Definitions:

class Users(Resource):
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

	def get(self):
		'''
		'''
		args_data = request.args.to_dict()
		print(args_data)

		vendor = args_data.get("vendor", "all")
		if vendor == "all":
			queries = {
				
			}
			columns = {
				
			}
		else:
			queries = {
				
			}
			columns = {
				
			}

		query_data = FlaskMongo.find('', columns, **queries)

		print(f'query_data: {query_data}')

		response = {
			"meta": self.meta,
			"vendors": query_data
		}
		return response, self.success_code, self.headers

	def post(self):
		'''
		'''
		try:
			post_data = request.get_json()

			users_data.load(post_data)
			name = post_data.get("name")
			mobile = post_data.get("mobile")
			print(post_data.keys())

			if not post_data:
				response = {
					"meta": self.meta,
					"message": "unable to process request",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_user_master'
			username = post_data.get("username")
			phone_no = post_data.get("phone_no")

			columns = {"_id": 0, "mobile": 1}
			queries = {"phone_no": phone_no}
			user_data = FlaskMongo.find(collection, columns, **queries)

			print(post_data)

			if user_data != []:
				response = {
					"meta": self.meta,
					"message": f"user {username} is already registered",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			post_data["no_free_trial"] = 2
			post_data["is_active"] = True
			FlaskMongo.insert(db, collection, post_data)

			response = {
				"meta": self.meta,
				"message": f"new user {name} added successfully",
				# "unique_id": post_data['unique_id'],
				"status": "success"
			}
			return response, self.success_code, self.headers

		except ValidationError as e:
			# raise e
			# print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
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

	def put(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			print(args_data)
			print(post_data)
			vendor = args_data.get("vendor")
			# print(f'condition: {(not vendor or post_data)}')

			if not vendor or not post_data:
				response = {
					"meta": self.meta,
					"message": "unable to process request",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			vendor_data.load(post_data, partial=True)

			updates = post_data
			queries = {
				"deleted": 0, "unique_id": vendor
			}
			FlaskMongo.update('vendor_details', updates, **queries)

			response = {
				"meta": self.meta,
				"message": f"vendor {vendor} updated successfully",
				"status": "success"
			}
			return response, self.success_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			return response, self.exception_code, self.headers