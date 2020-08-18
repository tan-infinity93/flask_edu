'''
'''

# Import Modules:

import json
from datetime import datetime
from flask import Flask, request, current_app as c_app
from flask_restful import Resource
from marshmallow import ValidationError
from bson.objectid import ObjectId
from app.schema import StudentUsers
from bindings.flask_mongo import FlaskMongo
from routes.teacher import TeacherUsers

studentusers_data = StudentUsers()

# Class Definitions:

class AdminUsers(TeacherUsers):
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
		self.account_type = "admin"
