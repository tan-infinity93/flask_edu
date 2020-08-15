'''
'''

# Import Modules:

import json
import jwt
from flask import request, current_app as c_app
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

# Middleware Decorators:

def is_valid_token(func):
	def function_wrapper(*args, **kwargs):
		"""
			WIP
		"""
		bad_code = 400
		auth_error_code = 401
		forbidden_error_code = 403
		process_error_code = 422
		server_error_code = 500
		response_headers = {"Content-Type": "application/json"}

		key = c_app.config.get('SECRET_KEY')
		auth_token = request.headers.get("Authorization")

		print(f'url: {request.path}')

		if auth_token:
			try:
				token_details = jwt.decode(auth_token, key, algorithms=['HS256'])
				print(f'token_details: {token_details}\n')
				response = token_details

				account_type = token_details.get("account_type")
				account_scope = c_app.config.get('SCOPES').get(account_type)

				print(f'account_scope: {account_scope}')

				if request.path not in account_scope:
					response = {
						'message': 'unable to process request', 
						'status': 'failure', 
						'reason': f'{account_type} user does not have sufficient permissions'
					}
					return response, forbidden_error_code, response_headers

			except ExpiredSignatureError as e:
				response = {'message': 'unable to process request', 'error': str(e), 'reason': 'jwt token expired'}
				return response, auth_error_code, response_headers

			except InvalidSignatureError as e:
				response = {'message': 'unable to process request', 'error' : str(e), 'reason': 'invalid jwt token'}
				return response, auth_error_code, response_headers

			except Exception as e:
				# raise e
				response = {'message': 'unable to process request', 'reason': 'server error'}
				return response, server_error_code, response_headers
		else:
			response = {
				'message': 'unable to process request',
				'status': 'failure',
				'reason': 'no Authorization token found in headers'
			}
			return response, bad_code, response_headers

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

		print(request.headers.get("Content-Type"))

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