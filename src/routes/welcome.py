'''
'''

# Import Modules:

from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource

# Class Definitions:

class Welcome(Resource):
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
		self.exception_code = 500

	def get(self):
		'''
		'''
		try:
			response = {
				"meta": self.meta,
				"message": "Welcome to edu api"
			}
			return response, self.success_code, self.headers

		except Exception as e:
			response = {
				"meta": self.meta,
				"message": "unable to process request"
			}
			return response, self.exception_code, self.headers