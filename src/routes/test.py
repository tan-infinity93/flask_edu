'''
'''

# Import Modules:

import json
import uuid
import math
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from app.schema import TestQuestionDetails, TestDeletion
from middleware.decorators import is_valid_args, is_valid_json, is_valid_token
from bindings.flask_mongo import FlaskMongo
from bindings.flask_logger import FlaskLogger
from utils.common_functions import format_api_error#get_uuid1, write_b64_to_file, save_file_to_s3

testquestion_data = TestQuestionDetails()
testdeletion_data = TestDeletion()

# Class Definitions:

class TestQuestionDetails(Resource):
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

	@is_valid_token
	@is_valid_args
	def get(self, **kwargs):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			print(args_data)

			testid = args_data.get("testid", "all")
			pageno = int(args_data.get("pageno", 1))
			room_name = args_data.get('room_name')
			cols = args_data.get('cols')
			teacher_id = kwargs.get("_id")

			collection1 = 'common_test_master'
			collection2 = 'common_question_master'

			if testid == "all":
				if pageno > 1:
					skip = 10 * (pageno - 1)
				else:
					skip = 0

				columns1 = {"_id": 0}
				queries1 = {"deleted": 0}
				query_data1 = FlaskMongo.find(
					collection1, columns1, queries1
				)

				total_count = len(query_data1)
				print(f'total_count: {total_count}\n')

				if cols:
					columns = cols.split(',')
					# print(f'\ncols: {cols}\n')
					# print(f'\ncols: {dict((k, 0) for k in cols)}\n')
					columns1 = {"_id": 0, "room_name": room_name}
					columns1.update(dict((k, 1) for k in columns))
					queries1 = {"deleted": 0, "teacher_id": teacher_id}
				else:
					columns = []
					columns1 = {"_id": 0, "room_name": room_name}
					queries1 = {"deleted": 0, "teacher_id": teacher_id}
				
				query_data2 = FlaskMongo.find(
					collection1, columns1, queries1, skip=skip, limit=10
				)

				data = {}

				print(f'query_data2: {query_data2}\n')

				if cols:
					if len(columns) == 1:
						select_column = columns[0]
						print(f'select_column: {select_column}')
						data = [
							d[select_column] for d in query_data2
						]
					else:
						data = query_data2
				else:
					for idx, qd1 in enumerate(query_data2):
						columns3 = {"_id": 0}
						queries3 = {"testid": qd1.get("id")}
						query_data3 = FlaskMongo.find(collection2, columns3, queries3)
						# print(f'query_data3: {query_data3}\n')
						# print(f'type: {type(query_data3)}\n')

						details = []

						for qd3 in query_data3:
							qd1.update(qd3)
							details.append(qd1)
						data[idx] = details

				total_pages = math.ceil(total_count/(10))

				test_data = {
					'total_count': total_count,
					'total': total_pages,
					'pageno': pageno,
					'previous': pageno - 1 if pageno > 1 and pageno <= total_pages else None,
					'next': pageno + 1 if pageno < total_pages else None,
					'data': data
				}

			else:
				queries1 = {
					"id": testid
				}
				columns1 = {"_id": 0}
				queries2 = {"testid": testid, "deleted": 0}
				columns2 = {"customerid": 0, "testid": 0}
				query_data1 = FlaskMongo.find(collection1, columns1, queries1)
				query_data2 = FlaskMongo.find(collection2, columns2, queries2)

				print(f'query_data1: {query_data1}\n')
				print(f'query_data2: {query_data2}\n')

				if query_data1 and query_data2:
					query_data1 = query_data1[0]
					query_data1['test_id'] = query_data1.pop('id')
					query_data1['qna'] = query_data2
					test_data = query_data1
				
				else:
					test_data = {}

			response = {
				"meta": self.meta,
				"test_data": test_data
			}
			FlaskLogger.log('get', 'tests_info', response, input_data=str(args_data), log_level='info')
			return response, self.success_code, self.headers

		except Exception as e:
			raise e
			print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('get', 'tests_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_json
	def post(self, **kwargs):
		"""
		"""
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()

			# print(post_data)
			print(f'kwargs: {kwargs}')

			testquestion_data.load(post_data)

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_master'
			collection2 = 'common_question_master'
			collection3 = 'common_user_master'

			customer_id = post_data.get('customerid')
			room_name = post_data.get('room_name')

			columns = {"_id": 0, "deleted": 0}
			queries = {"_id": ObjectId(customer_id)}
			user_data = FlaskMongo.find(collection3, columns, queries)

			if not user_data:
				response = {
					"meta": self.meta,
					"message": f"user with id {customer_id} does not exists",
					"status": "failure"
				}
				FlaskLogger.log('post', 'add_tests_info', response, input_data=str(post_data), log_level='info')
				return response, self.bad_code, self.headers

			elif user_data[0].get("account_type") != 'teacher':
				response = {
					"meta": self.meta,
					"message": f"user with id {customer_id} is not allowed to create tests",
					"status": "failure"
				}
				FlaskLogger.log('post', 'add_tests_info', response, input_data=str(post_data), log_level='info')
				return response, self.process_error_code, self.headers

			elif user_data[0].get("no_free_trial") < 1:
				response = {
					"meta": self.meta,
					"message": f"user with id {customer_id} has 0 trials left. Please renew subscription.",
					"status": "failure"
				}
				FlaskLogger.log('post', 'add_tests_info', response, input_data=str(post_data), log_level='info')
				return response, self.process_error_code, self.headers

			else:
				testid = str(uuid.uuid1()).replace("-", "")
				teacher_id = kwargs.get("_id")

				data1 = {
					"id": testid,
					"teacher_id": teacher_id,
					"room_name": room_name,
					"details": post_data.get("details"),
					"schedule": post_data.get("schedule"),
					"duration": post_data.get("duration"),
					"start_time": post_data.get("start_time"),
					"end_time": post_data.get("end_time"),
					"no_mandatory_questions": post_data.get("no_mandatory_questions"),
					"deleted": 0
				}
				FlaskMongo.insert(db, collection1, data1)
				
				for qna in post_data.get("qna"):
					data2 = {
						"customerid": post_data.get("customerid"),
						"testid": testid,
						"question": qna.get("question"),
						"option1": qna.get("options")[0],
						"option2": qna.get("options")[1],
						"option3": qna.get("options")[2],
						"option4": qna.get("options")[3],
						"answer": qna.get("answer"),
						"deleted": 0
					}
					FlaskMongo.insert(db, collection2, data2)

				no_free_trial = user_data[0].get("no_free_trial")
				if no_free_trial > 0:
					no_free_trial = no_free_trial - 1

					queries = {"_id": ObjectId(customer_id)}
					updates = {
						"no_free_trial": no_free_trial
					}
					FlaskMongo.update(collection3, updates, queries)

				response = {
					"meta": self.meta,
					"message": f"new test with id {testid} created successfully",
					"status": "success"
				}
				FlaskLogger.log('post', 'add_tests_info', response, input_data=str(post_data), log_level='info')
				return response, self.success_code, self.headers

		except ValidationError as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
			}
			FlaskLogger.log('post', 'add_tests_info', response, input_data=str(post_data), log_level='error')
			return response, self.bad_code, self.headers
		
		except Exception as e:
			# raise e
			# print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
			}
			FlaskLogger.log('post', 'add_tests_info', response, input_data=str(post_data), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_args
	@is_valid_json
	def put(self, **kwargs):
		'''
			Issue: check time validators, works in post request
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()

			print(post_data)
			print(args_data)

			args_data.update(post_data)
			testquestion_data.load(post_data, partial=True)

			test_id = args_data.get("testid")
			queries = {
				'id': test_id, "deleted": 0
			}
			columns = {
				'_id': 0
			}
			collection = 'common_test_master'
			query_data = FlaskMongo.find(collection, columns, queries)

			if not query_data:
				response = {
					"meta": self.meta,
					"message": f"test with id {test_id} does not exists",
					"status": "failure",
				}
				FlaskLogger.log('put', 'mod_tests_info', response, input_data=str({'ad':args_data, 'pd':post_data}), log_level='info')
				return response, self.bad_code, self.headers

			collection1 = 'common_test_master'
			collection2 = 'common_question_master'

			updates1 = {
				"id": test_id,
				"details": post_data.get("details"),
				"schedule": post_data.get("schedule"),
				"duration": post_data.get("duration"),
				"start_time": post_data.get("start_time"),
				"end_time": post_data.get("end_time"),
				"no_mandatory_questions": post_data.get("no_mandatory_questions")
			}
			queries1 = {
				"id": test_id
			}
			FlaskMongo.update(collection1, updates1, queries1)
			
			for qna in post_data.get("qna"):
				data2 = {
					"customerid": post_data.get("customerid"),
					"testid": test_id,
					"question": qna.get("question"),
					"option1": qna.get("options")[0],
					"option2": qna.get("options")[1],
					"option3": qna.get("options")[2],
					"option4": qna.get("options")[3],
					"answer": qna.get("answer")
				}
				updates2 = data2
				queries2 = {
					"_id": ObjectId(qna.get("_id")), "testid": test_id, "customerid": data2.get("customerid")
				}
				FlaskMongo.update(collection2, updates2, queries2)

			response = {
				"meta": self.meta,
				"message": f"test with id {test_id} updated successfully",
				"status": "success"
			}
			FlaskLogger.log('put', 'mod_tests_info', response, input_data=str({'ad':args_data, 'pd':post_data}), log_level='info')
			return response, self.success_code, self.headers

		except ValidationError as e:
			print(f'exception: {e}\n')
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
			}
			FlaskLogger.log('put', 'mod_tests_info', response, input_data=str({'ad':args_data, 'pd':post_data}), log_level='error')
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
			FlaskLogger.log('put', 'mod_tests_info', response, input_data=str({'ad':args_data, 'pd':post_data}), log_level='warning')
			return response, self.exception_code, self.headers

	@is_valid_token
	@is_valid_args
	def delete(self, **kwargs):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			# testquestion_data.load(args_data, partial=True)

			test_id = args_data.get("testid")
			queries = {'id': test_id, "deleted": 0}
			columns = {'_id': 0}
			collection1 = 'common_test_master'
			test_data = FlaskMongo.find(collection1, columns, queries)

			if not test_data:
				response = {
					"meta": self.meta,
					"message": f"test with id {test_id} does not exists",
					"status": "failure",
				}
				FlaskLogger.log('delete', 'del_tests_info', response, input_data=str(args_data), log_level='info')
				return response, self.bad_code, self.headers

			elif test_data:
				test_data = test_data[0]
				if test_data.get('deleted') == 1:
					response = {
						"meta": self.meta,
						"message": f"test with id {test_id} does not exists",
						"status": "failure",
					}
					FlaskLogger.log('delete', 'del_tests_info', response, input_data=str(args_data), log_level='info')
					return response, self.bad_code, self.headers

			updates1 = {"deleted": 1}
			queries1 = {"id": test_id}
			FlaskMongo.update(collection1, updates1, queries1)

			collection2 = 'common_question_master'
			updates2 = {"deleted": 1}
			queries2 = {"testid": test_id}
			FlaskMongo.update(collection2, updates2, queries2)

			response = {
				"meta": self.meta,
				"message": f"test with id {test_id} has been deleted",
				"status": "success",
			}
			FlaskLogger.log('delete', 'del_tests_info', response, input_data=str(args_data), log_level='info')
			return response, self.success_code, self.headers
		
		except ValidationError as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
			}
			FlaskLogger.log('delete', 'del_tests_info', response, input_data=str(args_data), log_level='error')
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
			FlaskLogger.log('delete', 'del_tests_info', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers

class UnDeleteTest(Resource):
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

	@is_valid_token
	@is_valid_json
	def post(self):
		"""
		"""
		try:
			post_data = request.get_json()

			# print(post_data)

			testdeletion_data.load(post_data)

			# Check for already exising entry:

			collection1 = 'common_test_master'
			collection2 = 'common_question_master'

			test_id = post_data.get('test_id')
			columns1 = {"_id": 0, "deleted": 0}
			queries1 = {"id": test_id}
			test_data = FlaskMongo.find(collection1, columns1, queries1)

			if not test_data:
				response = {
					"meta": self.meta,
					"message": f"test with id {test_id} does not exists",
					"status": "failure"
				}
				FlaskLogger.log('delete', 'undo_del_tests', response, input_data=str(args_data), log_level='info')
				return response, self.bad_code, self.headers
			else:
				queries1 = {"id": test_id}
				updates1 = {"deleted": 0}
				FlaskMongo.update(collection1, updates1, queries1)
				
				collection2 = 'common_question_master'
				updates2 = {"deleted": 0}
				queries2 = {"testid": test_id}
				FlaskMongo.update(collection2, updates2, queries2)

				response = {
					"meta": self.meta,
					"message": f"test with id {test_id} undeleted successfully",
					"status": "success"
				}
				FlaskLogger.log('delete', 'undo_del_tests', response, input_data=str(args_data), log_level='info')
				return response, self.success_code, self.headers

		except ValidationError as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
			}
			FlaskLogger.log('delete', 'undo_del_tests', response, input_data=str(args_data), log_level='error')
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
			FlaskLogger.log('delete', 'undo_del_tests', response, input_data=str(args_data), log_level='warning')
			return response, self.exception_code, self.headers