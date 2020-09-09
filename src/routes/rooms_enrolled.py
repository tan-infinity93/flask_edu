'''
'''

# Import Modules:

import math
import json
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from middleware.decorators import is_valid_args, is_valid_json, is_valid_token
from bindings.flask_mongo import FlaskMongo
from bindings.flask_logger import FlaskLogger
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

	@is_valid_token
	@is_valid_args
	def get(self, **kwargs):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			print(args_data)

			room_id = args_data.get("room_id", "all")
			teacher_id = args_data.get("teacher_id")
			pageno = int(args_data.get("pageno", 1))
			groupby_aggregate = args_data.get('groupby_aggregate', 'no')

			if room_id == "all":
				if pageno > 1:
					skip = 10 * (pageno - 1)
				else:
					skip = 0

				if teacher_id == "all":
					queries = {"deleted": 0}
				else:
					queries = {"deleted": 0, "teacher_id": teacher_id}
				
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_enroll_master'
				query_data = FlaskMongo.find(collection, columns, queries)

				total_count = len(query_data)

				if groupby_aggregate == 'yes':
					columns = {'_id': 0}
					queries = {}
					aggregate_pipeline = [
						{
							'$group': {
								'_id': '$room_id', 
								'student_names': {'$addToSet': '$name'}, 
								'count': {'$sum': 1}
							}
						}
					]
					query_data1 = FlaskMongo.find(collection, columns, queries, aggregate=aggregate_pipeline)
				
				else:
					queries1 = {"deleted": 0, "teacher_id": teacher_id}
					columns1 = {"_id": 0, "deleted": 0}
					query_data1 = FlaskMongo.find(
						collection, columns1, queries1, skip=skip, limit=10
					)

				total_pages = math.ceil(total_count/(10))

				rooms_enroll_data = {
					'total_count': total_count,
					'total': total_pages,
					'pageno': pageno,
					'previous': pageno - 1 if pageno > 1 and pageno <= total_pages else None,
					'next': pageno + 1 if pageno < total_pages else None,
			        'data': query_data1
				}
			
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

				rooms_enroll_data = query_data

			print(f'query_data: {query_data}')

			response = {
				"meta": self.meta,
				"rooms_enrollment": rooms_enroll_data
			}
			FlaskLogger.log('get', 'rooms_enrol_info', response, input_data=str(args_data), log_level='info')
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
			FlaskLogger.log('get', 'rooms_enrol_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_json
	def post(self, **kwargs):
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
				FlaskLogger.log('post', 'add_rooms_enroll_info', response, input_data=str(post_data), log_level='info')
				return response, self.bad_code, self.headers

			if user_data == []:
				response = {
					"meta": self.meta,
					"message": f"student with id {student_id} does not exists",
					"status": "failure",
				}
				FlaskLogger.log('post', 'add_rooms_enroll_info', response, input_data=str(post_data), log_level='info')
				return response, self.bad_code, self.headers

			if room_enrolled_data != []:
				response = {
					"meta": self.meta,
					"message": f"student with id {student_id} already enrolled in room with id {room_id}",
					"status": "failure",
				}
				FlaskLogger.log('post', 'add_rooms_enroll_info', response, input_data=str(post_data), log_level='info')
				return response, self.bad_code, self.headers

			post_data["name"] = user_data[0].get('name')
			post_data["banned"] = 0
			post_data["deleted"] = 0
			post_data["created"] = datetime.now().isoformat()
			FlaskMongo.insert(db, collection3, post_data)

			response = {
				"meta": self.meta,
				"message": f"student with id {student_id} added to room with id {room_id} successfully",
				"status": "success"
			}
			FlaskLogger.log('post', 'add_rooms_enroll_info', response, input_data=str(post_data), log_level='info')
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
			FlaskLogger.log('post', 'add_rooms_enroll_info', response, input_data=str(post_data), log_level='error')
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
			FlaskLogger.log('post', 'add_rooms_enroll_info', response, input_data=str(post_data), log_level='warning')
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
			
			args_data.update(post_data)
			rooms_enrolled_data.load(post_data, partial=True)

			######

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_room_enroll_master'
			
			room_id = args_data.get("room_id")
			teacher_id = args_data.get("teacher_id")
			student_id = post_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"student_id": student_id, "room_id": room_id
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
				FlaskLogger.log('post', 'mod_rooms_enroll_info', response, input_data=str(args_data, post_data), log_level='info')
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
			FlaskLogger.log('post', 'mod_rooms_enroll_info', response, input_data=str(args_data, post_data), log_level='info')
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
			FlaskLogger.log('post', 'mod_rooms_enroll_info', response, input_data=str(args_data, post_data), log_level='error')
			return response, self.bad_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('post', 'mod_rooms_enroll_info', response, input_data=str(args_data, post_data), log_level='warning')
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
			print(post_data)
			room_id = args_data.get("room_id")
			student_id = args_data.get("student_id")
			# print(f'condition: {(not user or post_data)}')

			columns = {"_id": 0}
			updates = {}
			queries = {
				"room_id": room_id, "student_id": student_id
			}
			collection = 'common_room_enroll_master'
			rooms_enrolled_data = FlaskMongo.find(collection, columns, queries)

			if not rooms_enrolled_data:
				response = {
					"meta": self.meta,
					"message": f"no enrollment found for student id {student_id} in room id {room_id}",
					"status": "failure",
				}
				FlaskLogger.log('delete', 'del_rooms_enroll_info', response, input_data=str(args_data), log_level='info')
				return response, self.bad_code, self.headers
			
			elif rooms_enrolled_data:
				rooms_enrolled_data = rooms_enrolled_data[0]
				if rooms_enrolled_data.get('deleted') == 1:
					response = {
						"meta": self.meta,
						"message": f"no enrollment found for student id {student_id} in room id {room_id}",
						"status": "failure",
					}

					FlaskLogger.log('delete', 'del_rooms_enroll_info', response, input_data=str(args_data), log_level='info')
					return response, self.bad_code, self.headers

			updates = {"deleted": 1}
			queries = {
				"room_id": room_id, "student_id": student_id
			}
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"enrollment for student id {student_id} in room id {room_id} deleted successfully",
				"status": "success"
			}
			FlaskLogger.log('delete', 'del_rooms_enroll_info', response, input_data=str(args_data), log_level='info')
			return response, self.success_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('delete', 'del_rooms_enroll_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers

