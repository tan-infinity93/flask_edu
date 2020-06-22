'''
'''

# Import Modules:

import json
from flask import request

# Middleware Decorators:

def is_valid_token(func):
	def function_wrapper(*args, **kwargs):
		"""
			WIP
		"""
		response_code = 422
		response_headers = {"Content-Type": "application/json"}

		# if not request.args.to_dict():
		# 	response = {
		# 		"message": "unable to process request",
		# 		"status": "failure",
		# 		"reason": "url arguments cannot be empty"
		# 	}
		# 	return response, response_code, response_headers
		return func(*args, **kwargs)
	return function_wrapper

def is_valid_args(func):
	def function_wrapper(*args, **kwargs):
		"""
		"""
		response_code = 422
		response_headers = {"Content-Type": "application/json"}

		if not request.args.to_dict():
			response = {
				"message": "unable to process request",
				"status": "failure",
				"reason": "url arguments cannot be empty"
			}
			return response, response_code, response_headers
		return func(*args, **kwargs)
	return function_wrapper

def is_valid_json(func):
	def function_wrapper(*args, **kwargs):
		"""
		"""
		response_code = 422
		response_headers = {"Content-Type": "application/json"}

		if request.headers.get("Content-Type") != "application/json":
			response = {
				"message": "unable to process request",
				"status": "failure",
				"reason": f"Content-Type 'application/json' expected, got {request.headers.get('Content-Type')}"
			}
			return response, response_code, response_headers

		if not request.get_json():
			response = {
				"message": "unable to process request",
				"status": "failure",
				"reason": "json cannot be empty"
			}
			return response, response_code, response_headers
		return func(*args, **kwargs)
	return function_wrapper