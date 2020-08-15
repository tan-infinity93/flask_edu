'''
'''

# Import Modules:

import json
import uuid
from datetime import datetime
from threading import Thread
from flask import Flask
from flask import current_app as c_app
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from bindings.flask_mongo import FlaskMongo
from bson.objectid import ObjectId
from middleware.decorators import is_valid_args, is_valid_json
from utils.common_functions import format_api_error
from utils.export_reports import PdfGenerator
from app.schema import Pdf
from bindings.flask_logger import FlaskLogger

pdf_schema = Pdf()

# Class Definitions:

class ReportsCreator(Resource):
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
		self.processing_code = 202
		self.bad_code = 400
		self.no_data_code = 404
		self.process_error_code = 422
		self.exception_code = 500

	@is_valid_json
	def post(self):
		'''
		'''
		try:
			post_data = request.get_json()
			pdf_schema.load(post_data, partial=True)

			file_name = post_data.get('file_name')
			url = post_data.get('url')
			file_path = post_data.get('file_path')
			string = post_data.get('string')

			pdf_generator = PdfGenerator(file_name)

			if url:
				source = 'url'
				# pdf_generator.parse_url(url)
				background_task = Thread(
					target=pdf_generator.parse_url, args=(url,)
				)
				background_task.daemon = True
				background_task.start()

			if file_path:
				source = 'file_path'
				# pdf_generator.parse_file(file_path)
				background_task = Thread(
					target=pdf_generator.parse_file, args=(file_path, )
				)
				background_task.daemon = True
				background_task.start()

			if string:
				source = 'string'
				# pdf_generator.parse_string(string)
				background_daemon_task = Thread(
					target=pdf_generator.parse_file, args=(string, )
				)
				background_task.daemon = True
				background_task.start()

			response = {
				'meta': self.meta,
				'status': 'success',
				'message': f'pdf generating from {source} successfully'
			}
			return response, self.processing_code, self.headers

		except ValidationError as e:
			# raise e
			# print(e)
			response = {
				"meta": self.meta,
				"message": "unable to process request",
				"status": "failure",
				"errors": format_api_error(e.messages)
			}
			FlaskLogger.log('post', 'create_pdf', response, input_data=str(post_data), log_level='error')
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
			FlaskLogger.log('post', 'create_pdf', response, input_data=str(post_data), log_level='warning')
			return response, self.exception_code, self.headers