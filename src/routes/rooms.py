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
from utils.common_functions import get_uuid1, format_api_error
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
			cols = args_data.get('cols')
			teacher_id = kwargs.get("_id")

			if room_id == "all":
				if pageno > 1:
					skip = 10 * (pageno - 1)
				else:
					skip = 0

				queries = {"deleted": 0, "teacher_id": teacher_id}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_master'
				query_data = FlaskMongo.find(collection, columns, queries)

				total_count = len(query_data)

				if cols:
					columns = cols.split(',')
					# print(f'\ncols: {cols}\n')
					# print(f'\ncols: {dict((k, 0) for k in cols)}\n')
					columns1 = {"_id": 0}
					columns1.update(dict((k, 1) for k in columns))
					queries1 = {"deleted": 0, "teacher_id": teacher_id}
				else:
					queries1 = {"deleted": 0, "teacher_id": teacher_id}
					columns1 = {"_id": 0, "deleted": 0}
				
				query_data1 = FlaskMongo.find(
					collection, columns1, queries1, skip=skip, limit=10
				)

				data = {}
				total_pages = math.ceil(total_count/(10))

				rooms_data = {
					'total_count': total_count,
					'total': total_pages,
					'pageno': pageno,
					'previous': pageno - 1 if pageno > 1 and pageno <= total_pages else None,
					'next': pageno + 1 if pageno < total_pages else None,
			        'data': query_data1
				}
			
			else:
				queries = {"deleted": 0, "teacher_id": teacher_id, "room_id": room_id}
				columns = {"_id": 0, "deleted": 0}
				collection = 'common_room_master'
				query_data = FlaskMongo.find(collection, columns, queries)
				if query_data:
					query_data = query_data[0]
				else:
					query_data = {}

				print(f'query_data: {query_data}')
				rooms_data = query_data

			
			response = {
				"meta": self.meta,
				"rooms_data": rooms_data
			}
			FlaskLogger.log('get', 'rooms_info', response, input_data=str(args_data), log_level='info')
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
			FlaskLogger.log('get', 'rooms_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_json
	def post(self, **kwargs):
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
				FlaskLogger.log('post', 'add_rooms_info', response, input_data=str(post_data), log_level='info')
				return response, self.bad_code, self.headers

			if room_data != []:
				response = {
					"meta": self.meta,
					"message": f"room {room_name} is already created",
					"status": "failure",
				}
				FlaskLogger.log('post', 'add_rooms_info', response, input_data=str(post_data), log_level='info')
				return response, self.bad_code, self.headers

			room_id = get_uuid1()
			post_data["room_id"] = room_id
			post_data["deleted"] = 0
			post_data["created"] = datetime.now().isoformat()
			FlaskMongo.insert(db, collection, post_data)

			response = {
				"meta": self.meta,
				"message": f"new room with id {room_id} added successfully",
				"status": "success"
			}
			FlaskLogger.log('post', 'add_rooms_info', response, input_data=str(post_data), log_level='info')
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
			FlaskLogger.log('post', 'add_rooms_info', response, input_data=str(post_data), log_level='error')
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
			FlaskLogger.log('post', 'add_rooms_info', response, input_data=str(post_data), log_level='warning')
			return response, self.exception_code, self.headers

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
			room_id = args_data.get("roomid")

			rooms_data.load(post_data, partial=True)

			######

			db = c_app.config.get('MONGO_DATABASE')
			collection = 'common_room_master'
			collection2 = 'common_user_master'
			teacher_id = args_data.get("teacherid")
			# room_name = post_data.get("room_name")

			columns = {"_id": 0}
			queries = {
				"teacher_id": teacher_id, "room_id": room_id
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
				FlaskLogger.log('put', 'mod_rooms_info', response, input_data=str({'ad': args_data, 'pd': post_data}), log_level='info')
				return response, self.bad_code, self.headers

			if room_data == []:
				response = {
					"meta": self.meta,
					"message": f"room with id {room_id} does not exists",
					"status": "failure",
				}
				FlaskLogger.log('put', 'mod_rooms_info', response, input_data=str({'ad': args_data, 'pd': post_data}), log_level='info')
				return response, self.bad_code, self.headers

			######

			updates = post_data
			queries = {
				"room_id": room_id
			}
			collection = 'common_room_master'
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"room with id {room_id} updated successfully",
				"status": "success"
			}
			FlaskLogger.log('put', 'mod_rooms_info', response, input_data=str({'ad': args_data, 'pd': post_data}), log_level='info')
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
			FlaskLogger.log('put', 'mod_rooms_info', response, input_data=str({'ad': args_data, 'pd': post_data}), log_level='error')
			return response, self.bad_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('put', 'mod_rooms_info', response, input_data=str({'ad': args_data, 'pd': post_data}), log_level='warning')
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
			room_id = args_data.get("room_id")

			columns = {"_id": 0}
			queries = {"room_id": room_id, "deleted": 0}
			collection = "common_room_master"

			room_data = FlaskMongo.find(collection, columns, queries)
			print(f'room_data: {room_data}')

			if not room_data:
				response = {
					"meta": self.meta,
					"message": f"room with id {room_id} does not exists",
					"status": "failure",
				}
				FlaskLogger.log('delete', 'del_rooms_info', response, input_data=str(args_data), log_level='info')
				return response, self.bad_code, self.headers
			
			elif room_data:
				room_data = room_data[0]
				if room_data.get('deleted') == 1:
					response = {
						"meta": self.meta,
						"message": f"room with id {room_id} does not exists",
						"status": "failure",
					}
					FlaskLogger.log('delete', 'del_rooms_info', response, input_data=str(args_data), log_level='info')
					return response, self.bad_code, self.headers

			updates = {"deleted": 1}
			queries = {"room_id": room_id}
			collection = 'common_room_master'
			FlaskMongo.update(collection, updates, queries)

			response = {
				"meta": self.meta,
				"message": f"room with id {room_id} deleted successfully",
				"status": "success"
			}
			FlaskLogger.log('delete', 'del_rooms_info', response, input_data=str(args_data), log_level='info')
			return response, self.success_code, self.headers

		except Exception as e:
			# raise e
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('delete', 'del_rooms_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers