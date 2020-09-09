'''
'''

# Import Modules:

import json
import math
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from app.schema import TeacherUsers
from middleware.decorators import is_valid_args, is_valid_json, is_valid_token
from bindings.flask_mongo import FlaskMongo
from bindings.flask_logger import FlaskLogger
from utils.common_functions import format_api_error #get_uuid1, write_b64_to_file, save_file_to_s3

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

	@is_valid_token
	@is_valid_args
	def get(self, **kwargs):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			print(args_data)

			user = args_data.get("user", "all")
			pageno = int(args_data.get("pageno", 1))
			if user == "all":
				if pageno > 1:
					skip = 10 * (pageno - 1)
				else:
					skip = 0
				queries = {"deleted": 0, "account_type": self.account_type}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_user_master'
				query_data1 = FlaskMongo.find(collection, columns, queries)

				queries = {"deleted": 0, "account_type": self.account_type}
				columns = {"_id": 0, "deleted": 0}
				query_data2 = FlaskMongo.find(collection, columns, queries, skip=skip, limit=10)

				total_count = len(query_data1)
				total_pages = math.ceil(total_count/(10))
				query_data = {
					'total': total_pages,
					'pageno': pageno,
					'previous': pageno - 1 if pageno > 1 and pageno <= total_pages else None,
					'next': pageno + 1 if pageno < total_pages else None,
					'data': query_data2
				}
			
			else:
				queries = {"_id": ObjectId(user), "deleted": 0, "account_type": self.account_type}
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
			FlaskLogger.log('get', f'{self.account_type}_info', response, input_data=str(args_data), log_level='info')
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
			FlaskLogger.log('get', f'{self.account_type}_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers

	# @is_valid_token
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
				FlaskLogger.log('post', f'add_{self.account_type}_info', response, input_data=str(post_data), log_level='info')
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
			FlaskLogger.log('post', f'add_{self.account_type}_info', response, input_data=str(post_data), log_level='info')
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
			FlaskLogger.log('post', f'add_{self.account_type}_info', response, input_data=str(post_data), log_level='error')
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
			FlaskLogger.log('post', f'add_{self.account_type}_info', response, input_data=str(post_data), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_args
	@is_valid_json
	def put(self, **kwargs):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			print(args_data)
			print(post_data)

			teacherusers_data.load(post_data, partial=True)
			user = args_data.get("user")

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
				FlaskLogger.log('put', f'mod_{self.account_type}_info', response, input_data=str(args_data, post_data), log_level='info')
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
			FlaskLogger.log('put', f'mod_{self.account_type}_info', response, input_data=str(args_data, post_data), log_level='info')
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
			FlaskLogger.log('put', f'mod_{self.account_type}_info', response, input_data=str(args_data, post_data), log_level='error')
			return response, self.bad_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('put', f'mod_{self.account_type}_info', response, input_data=str(args_data, post_data), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_args
	def delete(self, **kwargs):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			print(args_data)
			# print(post_data)

			teacherusers_data.load(args_data, partial=True)
			userid = args_data.get("userid")
			# user = args_data.get("user", "all")
			# print(f'condition: {(not user or post_data)}')

			columns = {"_id": 0}
			queries = {"_id": ObjectId(userid)}
			collection = "common_user_master"

			user_data = FlaskMongo.find(collection, columns, queries)
			print(f'user_data: {user_data}')

			if not user_data:
				response = {
					"meta": self.meta,
					"message": f"user with id {userid} does not exists",
					"status": "failure",
				}
				FlaskLogger.log('delete', f'del_{self.account_type}_info', response, input_data=str(args_data), log_level='info')
				return response, self.bad_code, self.headers
			
			elif user_data:
				user_data = user_data[0]
				if user_data.get('deleted') == 1:
					response = {
						"meta": self.meta,
						"message": f"user with id {userid} does not exists",
						"status": "failure",
					}
					FlaskLogger.log('delete', f'del_{self.account_type}_info', response, input_data=str(args_data), log_level='info')
					return response, self.bad_code, self.headers

			updates = {"deleted": 1}
			queries = {
				"_id": ObjectId(userid)
			}
			collection = 'common_user_master'
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"user with id {userid} deleted successfully",
				"status": "success"
			}
			FlaskLogger.log('delete', f'del_{self.account_type}_info', response, input_data=str(args_data), log_level='info')
			return response, self.success_code, self.headers

		except ValidationError as e:
			# raise e
			print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"errors": format_api_error(e.messages)
			}
			FlaskLogger.log('delete', f'del_{self.account_type}_info', response, input_data=str(args_data), log_level='error')
			return response, self.bad_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('delete', f'del_{self.account_type}_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers