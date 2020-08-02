'''
'''

# Import Modules:

import json
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from middleware.decorators import is_valid_args, is_valid_json
from bindings.flask_mongo import FlaskMongo
from utils.common_functions import get_uuid1, format_api_error
from app.schema import RoomsEnrolled

rooms_enrolled_data = RoomsEnrolled()

# Class Definitions:

class RoomsEnrolled(Resource):
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

			room_id = args_data.get("roomid", "all")
			teacher_id = args_data.get("teacherid")

			if room_id == "all":
				if teacher_id == "all":
					queries = {"deleted": 0}
				else:
					queries = {"deleted": 0, "teacher_id": teacher_id}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_enroll_master'
				query_data = FlaskMongo.find(collection, columns, queries)
			
			else:
				if teacher_id == "all":
					queries = {"deleted": 0, "room_id": room_id}
				else:
					queries = {"deleted": 0, "teacher_id": teacher_id, "room_id": room_id}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_enroll_master'
				query_data = FlaskMongo.find(collection, columns, queries)
				if query_data:
					if len(query_data) == 1:
						query_data = query_data[0]
				else:
					query_data = {}

			print(f'query_data: {query_data}')

			response = {
				"meta": self.meta,
				"rooms_enrollment": query_data
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

			rooms_enrolled_data.load(post_data)
			print(post_data.keys())

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_room_master'
			collection2 = 'common_user_master'
			collection3 = 'common_room_enroll_master'
			
			teacher_id = post_data.get("teacher_id")
			room_id = post_data.get("room_id")
			student_id = post_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"teacher_id": teacher_id, "room_id": room_id
			}
			queries2 = {
				"_id": ObjectId(student_id)
			}
			queries3 = {
				"student_id": student_id, "teacher_id": teacher_id, "room_id": room_id
			}
			room_data = FlaskMongo.find(collection, columns, queries)
			user_data = FlaskMongo.find(collection2, columns, queries2)
			room_enrolled_data = FlaskMongo.find(collection3, columns, queries3)

			print(post_data)
			print(f'room_data: {room_data}')

			if room_data == []:
				response = {
					"meta": self.meta,
					"message": f"teacher with id {teacher_id} has not created room with id {room_id}",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			if user_data == []:
				response = {
					"meta": self.meta,
					"message": f"student with id {student_id} does not exists",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			if room_enrolled_data != []:
				response = {
					"meta": self.meta,
					"message": f"student with id {student_id} already enrolled in room with id {room_id}",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			post_data["banned"] = False
			post_data["deleted"] = 0
			post_data["created"] = datetime.now().isoformat()
			FlaskMongo.insert(db, collection3, post_data)

			response = {
				"meta": self.meta,
				"message": f"student with id {student_id} added to room with id {room_id} successfully",
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
			
			args_data.update(post_data)
			rooms_enrolled_data.load(post_data, partial=True)

			######

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_room_enroll_master'
			
			room_id = args_data.get("roomid")
			teacher_id = args_data.get("teacherid")
			student_id = post_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"teacher_id": teacher_id, "room_id": room_id
			}
			room_enrolled_data = FlaskMongo.find(collection, columns, queries)

			# print(post_data)
			print(f'room_data: {room_enrolled_data}')

			if room_enrolled_data == []:
				response = {
					"meta": self.meta,
					"message": f"rooms enrollment for id {room_id} does not exists",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			######

			updates = post_data
			queries = {
				"room_id": room_id, "student_id": student_id
			}
			collection = 'common_room_enroll_master'
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"rooms enrollment with room id {room_id} updated successfully",
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