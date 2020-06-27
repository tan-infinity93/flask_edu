'''
'''

# Import Modules:

from flask import Flask, request, current_app as c_app
from flask_restful import Resource
# from app.flask_mongo import FlaskMongo

# Class Definitions:

class Welcome(Resource):
	'''
	'''
	def __init__(self):
		'''
		'''
		self.headers = {"Content-Type": "application/json"}
		self.success_code = 200
		self.bad_code = 400
		self.exception_code = 500

	def get(self):
		'''
		'''
		try:
			response = {"message": "Welcome to edu api"}
			return response, self.success_code, self.headers

		except Exception as e:
			response = {"message": "unable to process request"}
			return response, self.exception_code, self.headers