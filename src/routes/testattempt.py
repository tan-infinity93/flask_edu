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
from app.schema import TestAttempt
from middleware.decorators import is_valid_args, is_valid_json, is_valid_token
from bindings.flask_mongo import FlaskMongo
from utils.common_functions import format_api_error # get_uuid1, write_b64_to_file, save_file_to_s3

testattempt_data = TestAttempt()

# Class Definitions:

class TestAttemptDetails(Resource):
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
	def get(self):
		'''
		'''
		try:
			pass

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

	@is_valid_token
	@is_valid_json
	def post(self):
		'''
			A Test Attempt can be new or redo
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			post_data.update(args_data)

			print(post_data)

			testattempt_data.load(post_data)
			student_name = post_data.get("student_name")
			phone_no = post_data.get("phone_no")

			print(post_data.keys())

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_student'
			collection2 = 'common_test_student_ques_answers'
			
			test_id = args_data.get("test_id")
			student_id = args_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"test_id": test_id, "student_id": student_id#, "is_complete": True
			}
			test_data = FlaskMongo.find(collection1, columns, queries)
			test_qna_data = FlaskMongo.find(collection2, columns, queries)

			print(post_data)

			if test_data and test_qna_data:
				response = {
					"meta": self.meta,
					"message": f"Test {test_id} is under progress",
					"status": "failure",
				}
				return response, self.bad_code, self.headers
			else:
				data1 = {
					"student_id": student_id,
					"test_id": test_id,
					"student_name": student_name,
					"phone_no": phone_no,
					"timestamp": datetime.now().isoformat()
				}
				FlaskMongo.insert(db, collection1, data1)

				data2 = [
					{
						"student_id": student_id,
						"test_id": test_id,
						"question_id": qa.get("_id"),
						"question": qa.get("question"),
						"answer": qa.get("answer"),
						"is_correct": qa.get("is_correct"),
						"timestamp": datetime.now().isoformat()
					}
					for qa in post_data.get('qna')
				]
			
				# Bulk Insert Records Here:

				FlaskMongo.insert(db, collection2, data2, bulk=True)

				response = {
					"meta": self.meta,
					"message": f"test with id {test_id} started successfully",
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

	@is_valid_token
	@is_valid_args
	@is_valid_json
	def put(self):
		'''
			A Test Attempt can be new or redo
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			post_data.update(args_data)

			print(post_data)

			testattempt_data.load(post_data, partial=True)
			student_name = post_data.get("student_name")
			phone_no = post_data.get("phone_no")
			is_complete = post_data.get("is_complete")

			print(post_data.keys())

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_student'
			collection2 = 'common_test_student_ques_answers'
			test_id = args_data.get("test_id")
			student_id = args_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"test_id": test_id, "student_id": student_id#, "is_complete": True
			}

			print(post_data)

			test_data = FlaskMongo.find(collection1, columns, queries)
			test_qna_data = FlaskMongo.find(collection2, columns, queries)

			print(post_data)

			if not test_data and not test_qna_data:
				response = {
					"meta": self.meta,
					"message": f"No data found for Test with {test_id}",
					"status": "failure",
				}
				return response, self.bad_code, self.headers
			else:
				queries1 = {
					"student_id": student_id,
					"test_id": test_id
				}
				updates1 = {
					"student_name": student_name,
					"phone_no": phone_no,
					# "is_complete": is_complete
				}
				# data1["created"] = datetime.now().isoformat()
				
				FlaskMongo.update(collection1, updates1, queries1)

				for qa in post_data.get('qna'):
					queries2 = {
						"student_id": student_id,
						"test_id": test_id,
						"question_id": qa.get("_id"),
						"question": qa.get("question"),
					}
					updates2 ={
						"answer": qa.get("answer"),
						"is_correct": qa.get("is_correct")
					}

					# updates2 ={}
					# if qa.get("option_selected"):
					# 	updates2.update({"answer": qa.get("option_selected")})
					# if qa.get("is_correct"):
					# 	updates2.update({"is_correct": qa.get("is_correct")})
			
					# Update Question Answers Here:

					FlaskMongo.update(collection2, updates2, queries2)

			response = {
				"meta": self.meta,
				"message": f"test attempt with {test_id} updated successfully",
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

class TestAttemptComplete(Resource):
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
	@is_valid_json
	def put(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()
			post_data.update(args_data)

			testattempt_data.load(post_data, partial=True)

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_student'
			collection2 = 'common_test_student_ques_answers'
			test_id = args_data.get("test_id")
			student_id = args_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"test_id": test_id, "student_id": student_id#, "is_complete": True
			}
			test_data = FlaskMongo.find(collection1, columns, queries)

			if not test_data:
				response = {
					"meta": self.meta,
					"message": "unable to process request",
					"status": "failure",
					"reason": f"No test with id {test_id} found for student id {student_id}"
				}
				return response, self.bad_code, self.headers
			else:
				updates1 = {
					'is_complete': post_data.get('is_complete')
				}
				queries1 = {
					"student_id": student_id, "test_id": test_id
				}
				FlaskMongo.update(collection1, updates1, queries1)

				response = {
					"meta": self.meta,
					"message": f"Test with id {test_id} updated for student id {student_id}",
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