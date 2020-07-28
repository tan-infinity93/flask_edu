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
from utils.common_functions import get_uuid1
from app.schema import Rooms

rooms_data = Rooms()

# Class Definitions:

class RoomsApi(Resource):
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

	@is_valid_args
	def get(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			print(args_data)

			room_id = args_data.get("room", "all")
			teacher_id = args_data.get("teacherid")

			if room_id == "all":
				queries = {"deleted": False, "teacher_id": teacher_id}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_master'
				query_data = FlaskMongo.find(collection, columns, queries)
			
			else:
				queries = {"deleted": False, "teacher_id": teacher_id, "room_id": room_id}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_master'
				query_data = FlaskMongo.find(collection, columns, queries)
				if query_data:
					query_data = query_data[0]
				else:
					query_data = {}

			print(f'query_data: {query_data}')

			response = {
				"meta": self.meta,
				"rooms": query_data
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

			rooms_data.load(post_data)
			print(post_data.keys())

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_room_master'
			collection2 = 'common_user_master'
			teacher_id = post_data.get("teacher_id")
			room_name = post_data.get("room_name")

			columns = {"_id": 0}
			queries = {
				"teacher_id": teacher_id, "room_name": room_name
			}
			queries2 = {
				"_id": ObjectId(teacher_id)
			}
			room_data = FlaskMongo.find(collection, columns, queries)
			user_data = FlaskMongo.find(collection2, columns, queries2)

			print(post_data)
			print(f'room_data: {room_data}')

			if user_data == []:
				response = {
					"meta": self.meta,
					"message": f"teacher with id {teacher_id} does not exists",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			if room_data != []:
				response = {
					"meta": self.meta,
					"message": f"room {room_name} is already created",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			room_id = get_uuid1()
			post_data["room_id"] = room_id
			post_data["deleted"] = False
			post_data["created"] = datetime.now().isoformat()
			FlaskMongo.insert(db, collection, post_data)

			response = {
				"meta": self.meta,
				"message": f"new room with id {room_id} added successfully",
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
			# raise e
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