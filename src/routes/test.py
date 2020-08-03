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
from app.schema import TestQuestionDetails
from middleware.decorators import is_valid_args, is_valid_json
from bindings.flask_mongo import FlaskMongo
from utils.common_functions import format_api_error#get_uuid1, write_b64_to_file, save_file_to_s3

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

	@is_valid_args
	def get(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			print(args_data)

			testid = args_data.get("testid", "all")
			collection1 = 'common_test_master'
			collection2 = 'common_question_master'

			if testid == "all":
				columns1 = {"_id": 0}
				queries1 = {}
				query_data1 = FlaskMongo.find(
					collection1, columns1, queries1
				)
				print(f'query_data1: {query_data1}\n')

				# testids = [test.get("id") for test in query_data1]
				test_data = {}

				for idx, qd1 in enumerate(query_data1):
					columns2 = {"_id": 0}
					queries2 = {"testid": qd1.get("id")}
					query_data2 = FlaskMongo.find(collection2, columns2, queries2)
					print(f'query_data2: {query_data2}\n')
					print(f'type: {type(query_data2)}\n')

					details = []

					for qd2 in query_data2:
						# qd2.pop("customerid")
						# qd2.pop("testid")
						
						# qd1.pop("id")
						qd1.update(qd2)

						print(f'td: {qd1}')
						details.append(
							qd1
						)
					test_data[idx] = details

			else:
				queries1 = {
					"id": testid
				}
				columns1 = {"_id": 0}
				queries2 = {"testid": testid}
				columns2 = {"customerid": 0, "testid": 0}

			
				query_data1 = FlaskMongo.find(collection1, columns1, queries1)
				query_data2 = FlaskMongo.find(collection2, columns2, queries2)

				# print(f'query_data1: {query_data1}\n')
				# print(f'query_data2: {query_data2}\n')

				query_data1 = query_data1[0]
				query_data1['test_id'] = query_data1.pop('id')
				query_data1['qna'] = query_data2
				test_data = query_data1

			response = {
				"meta": self.meta,
				"test_data": test_data
			}
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
			return response, self.exception_code, self.headers

	@is_valid_json
	def post(self):
		"""
		"""
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()

			# print(post_data)

			testquestion_data.load(post_data)

			# Check for already exising entry:

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_master'
			collection2 = 'common_question_master'
			collection3 = 'common_user_master'

			customer_id = post_data.get('customerid')
			columns = {"_id": 0, "deleted": 0}
			queries = {"_id": ObjectId(customer_id)}
			user_data = FlaskMongo.find(collection3, columns, queries)

			if not user_data:
				response = {
					"meta": self.meta,
					"message": f"user with id {customer_id} does not exists",
					"status": "failure"
				}
				return response, self.bad_code, self.headers

			elif user_data[0].get("account_type") != 'teacher':
				response = {
					"meta": self.meta,
					"message": f"user with id {customer_id} is not allowed to create tests",
					"status": "failure"
				}
				return response, self.process_error_code, self.headers

			elif user_data[0].get("no_free_trial") < 1:
				response = {
					"meta": self.meta,
					"message": f"user with id {customer_id} has 0 trials left. Please renew subscription.",
					"status": "failure"
				}
				return response, self.process_error_code, self.headers

			else:
				testid = str(uuid.uuid1()).replace("-", "")

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
				return response, self.success_code, self.headers

		except ValidationError as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
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
			Issue: check time validators, works in post request
		'''
		try:
			args_data = request.args.to_dict()
			post_data = request.get_json()

			print(post_data)
			print(args_data)

			args_data.update(post_data)
			testquestion_data.load(post_data, partial=True)

			test_id = args_data.get("test_id")
			queries = {
				'id': test_id
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
				return response, self.bad_code, self.headers

			####
			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_test_master'
			collection2 = 'common_question_master'

			data1 = {
				"id": test_id,
				"details": post_data.get("details"),
				"schedule": post_data.get("schedule"),
				"duration": post_data.get("duration"),
				"start_time": post_data.get("start_time"),
				"end_time": post_data.get("end_time"),
				"no_mandatory_questions": post_data.get("no_mandatory_questions")
			}
			updates1 = data1
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
			####

			response = {
				"meta": self.meta,
				"message": f"test with id {test_id} updated successfully",
				"status": "success"
			}
			return response, self.success_code, self.headers

		except ValidationError as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"reason": format_api_error(e.messages)
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