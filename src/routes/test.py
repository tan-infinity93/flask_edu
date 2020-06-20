'''
'''

# Import Modules:

import json
import uuid
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from app.schema import TestQuestionDetails
from bindings.flask_mongo import FlaskMongo
# from utils.common_functions import get_uuid1, write_b64_to_file, save_file_to_s3

testquestion_data = TestQuestionDetails()

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

		query_data1 = FlaskMongo.find('', columns, **queries)
		query_data2 = FlaskMongo.find('', columns, **queries)

		print(f'query_data1: {query_data1}')
		print(f'query_data2: {query_data2}')

		response = {
			"meta": self.meta,
			# "vendors": query_data
		}
		return response, self.success_code, self.headers

	def post(self):
		"""
		"""
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()

			print(post_data)

			if not post_data:
				response = {
					"meta": self.meta,
					"message": "unable to process request",
					"status": "failure",
				}
				return response, self.bad_code, self.headers

			testquestion_data.load(post_data)

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_master'
			collection2 = 'common_question_master'

			print(post_data)

			testid = str(uuid.uuid1())#.replace("-", "")

			data1 = {
				"id": testid,
				"details": post_data.get("details"),
				"schedule": post_data.get("schedule"),
				"duration": post_data.get("duration"),
				"start_time": post_data.get("start_time"),
				"end_time": post_data.get("end_time"),
				"no_mandatory_questions": post_data.get("no_mandatory_questions")
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
					"answer": qna.get("answer")
				}
				FlaskMongo.insert(db, collection2, data2)

			response = {
				"meta": self.meta,
				"message": f"new test with id {testid} created successfully",
				"status": "success"
			}
			return response, self.success_code, self.headers

		except ValidationError as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": str(e)
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