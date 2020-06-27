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
from middleware.decorators import is_valid_args, is_valid_json
from bindings.flask_mongo import FlaskMongo
# from utils.common_functions import get_uuid1, write_b64_to_file, save_file_to_s3

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

	@is_valid_json
	def put(self):
		'''
			A Test Attempt can be new or redo
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()

			testattempt_data.load(post_data)
			name = post_data.get("name")
			print(post_data.keys())

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_student'
			test_id = post_data.get("test_id")
			student_id = post_data.get("student_id")

			columns = {"_id": 0}
			queries = {
				"test_id": test_id, "student_id": student_id, "is_complete": True
			}
			test_data = FlaskMongo.find(collection1, columns, **queries)

			print(post_data)

			# if not test_data:
			# 	response = {
			# 		"meta": self.meta,
			# 		"message": f"Test {test_id} is already completed",
			# 		"status": "failure",
			# 	}
			# 	return response, self.bad_code, self.headers

			# post_data["account_type"] = self.account_type
			# post_data["no_free_trial"] = 2
			# post_data["is_active"] = True
			# post_data["deleted"] = 0

			collection2 = 'common_test_student_ques_answers'

			data1 = {
				"student_id": "cacasca",
				"test_id": "evwvew",
				"student_name": "acasac",
				"phone_no": "wvevw",
				"is_complete": True,
			}
			data1["created"] = datetime.now().isoformat()
			FlaskMongo.insert(db, collection1, data1)

			data2 = [
				{
					"student_id": student_id,
					"test_id": test_id,
					"question_id": qa.get("question_id"),
					"option_selected": qa.get("option_selected"),
					"is_correct": qa.get("is_correct")
				}
				for qa in post_data.get('qna')
			]
			
			# Bulk Insert Records Here:

			FlaskMongo.insert(db, collection2, data2, bulk=True)

			response = {
				"meta": self.meta,
				"message": f"test with {test_id} added successfully",
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
				"errors": e.messages
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