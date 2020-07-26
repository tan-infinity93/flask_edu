'''
'''

# Import Modules:

import json
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from app.schema import TeacherUsers
from middleware.decorators import is_valid_args, is_valid_json
from bindings.flask_mongo import FlaskMongo
# from utils.common_functions import get_uuid1, write_b64_to_file, save_file_to_s3

teacherusers_data = TeacherUsers()

# Class Definitions:

class TeacherUsers(Resource):
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
		self.account_type = "teacher"

	def get(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			print(args_data)

			user = args_data.get("user", "all")
			if user == "all":
				queries = {"deleted": 0, "account_type": self.account_type}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_user_master'
				query_data = FlaskMongo.find(collection, columns, queries)
			
			else:
				queries = {"_id": ObjectId(user), "deleted": 0, "account_type": "teacher"}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_user_master'
				query_data = FlaskMongo.find(collection, columns, queries)
				if query_data:
					query_data = query_data[0]
				else:
					query_data = {}

			print(f'query_data: {query_data}')

			response = {
				"meta": self.meta,
				"users": query_data
			}
			return response, self.success_code, self.headers

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

	@is_valid_json
	def post(self):
		'''
		'''
		try:
			post_data = request.get_json()

			teacherusers_data.load(post_data)
			name = post_data.get("name")
			# mobile = post_data.get("mobile")
			print(post_data.keys())

			# if not post_data:
			# 	response = {
			# 		"meta": self.meta,
			# 		"message": "unable to process request",
			# 		"status": "failure",
			# 	}
			# 	return response, self.bad_code, self.headers

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_user_master'
			username = post_data.get("username")
			phone_no = post_data.get("phone_no")

			columns = {"_id": 0}
			queries = {"phone_no": phone_no}
			user_data = FlaskMongo.find(collection, columns, queries)

			print(post_data)

			if user_data != []:
				response = {
					"meta": self.meta,
					"message": f"user {username} is already registered",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			post_data["account_type"] = self.account_type
			post_data["no_free_trial"] = 2
			post_data["is_active"] = True
			post_data["deleted"] = 0
			post_data["created"] = datetime.now().isoformat()
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
				"errors": format_api_error(e.messages)
			}
			return response, self.bad_code, self.headers

		except Exception as e:
			raise e
			print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			return response, self.exception_code, self.headers

	@is_valid_args
	@is_valid_json
	def put(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			print(args_data)
			print(post_data)
			user = args_data.get("user")
			# user = args_data.get("user", "all")
			# print(f'condition: {(not user or post_data)}')

			if not user or not post_data:
				response = {
					"meta": self.meta,
					"message": "unable to process request",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			teacherusers_data.load(post_data, partial=True)

			columns = {"_id": 0}
			queries = {"_id": ObjectId(user)}
			collection = 'common_user_master'
			user_data = FlaskMongo.find(collection, columns, queries)

			if user_data == []:
				response = {
					"meta": self.meta,
					"message": f"user {user} does not exists",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			updates = post_data
			queries = {
				"_id": ObjectId(user)
			}
			collection = 'common_user_master'
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"user {user} updated successfully",
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

	def delete(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			print(args_data)
			print(post_data)
			user = args_data.get("user")
			# user = args_data.get("user", "all")
			# print(f'condition: {(not user or post_data)}')

			if not user:
				response = {
					"meta": self.meta,
					"message": "unable to process request",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			updates = {"delete": 0}
			queries = {
				"_id": ObjectId(user)
			}
			collection = 'common_user_master'
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"user {user} updated successfully",
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