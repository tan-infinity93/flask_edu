'''
'''

# Import Modules:

import json
import uuid
from datetime import datetime

from flask import Flask
from flask import current_app as c_app
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from bindings.flask_mongo import FlaskMongo
from bson.objectid import ObjectId
from middleware.decorators import is_valid_args, is_valid_json
from utils.common_functions import format_api_error

# Class Definitions:

class RoomsStats(Resource):
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
		self.no_data_code = 404
		self.process_error_code = 422
		self.exception_code = 500

	# @is_valid_args
	def get(self):
		'''
		'''
		try:
			args_data = request.args.to_dict()
			test_id = args_data.get('testid')

			db = c_app.config.get('MONGO_DATABASE')
			collection1 = 'common_room_master'

			columns = {'_id': 0}
			queries = {}
			aggregate_pipeline = [
				{
					'$group': {
						'_id': '$room_id',
						'count': { '$sum': 1 }
					}
				}
			]
			room_counts = FlaskMongo.find(collection1, columns, queries, aggregate=aggregate_pipeline)

			# columns = {'_id': 0}
			# queries = {}
			# distinct_column = 'institute_name'
			# institute_names = FlaskMongo.find(
			# 	collection1, columns, queries, distinct=True, distinct_column=distinct_column
			# )

			total_rooms = db[collection1].find({}).count()
			deleted_rooms = db[collection1].find({"deleted": 1}).count()
			rooms = {
				'total': total_rooms,
				'deleted': deleted_rooms,
				'active': total_rooms - deleted_rooms
			}

			columns = {'room_id': 1}
			queries = {}
			rooms_ids = FlaskMongo.find(collection1, columns, queries)
			rooms_ids = [rid.get('_id') for rid in rooms_ids]

			columns = {'_id': 0, 'room_id': 1, 'limit': 1}
			queries = {}
			rooms_limits = FlaskMongo.find(collection1, columns, queries)
			rooms_limits = [rid for rid in rooms_limits]

			stats = {
				'rooms_ids': rooms_ids,
				'rooms': rooms,
				'room_counts': room_counts,
				'rooms_limits': rooms_limits
				# 'institute_names': institute_names
			}

			response = {
				"meta": self.meta,
				"status": "success",
				"stats": stats
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