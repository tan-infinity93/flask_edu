'''
'''

# Import Modules:

import os
import uuid
import time
import base64
import secrets
import jwt
import boto3
from flask import current_app as c_app

# Function Definitions:

def get_uuid1():
	try:
		return str(uuid.uuid1())
	except Exception as e:
		raise e

def format_api_error(error):
	'''
	'''
	try:
		errors = {}
		for k, v in error.items():
			errors[k] = v[0]
		return errors

	except Exception as e:
		print(e)

def generate_auth_token(payload):
	'''
	'''
	try:
		key = c_app.config.get('SECRET_KEY')
		headers = {'kid': secrets.token_hex(10)}
		token = jwt.encode(payload, key, algorithm='HS256', headers=headers)
		token = token.decode('UTF-8')
		print(type(token))
		return token

	except Exception as e:
		print(e)

def write_b64_to_file(path, b64_str, file_name, mobile, name):
	try:
		file_path = path + "\\"
		print(file_path)

		if 'jpg' or 'jpeg' in b64_str:
			file_extension = 'jpg'
			replace = 'data:image/jpeg;base64,'
		
		if 'png' in b64_str:
			file_extension = 'png'
			replace = 'data:image/png;base64,'

		file_with_extension = mobile + '_' + name.replace(' ', '_').lower() + '_' + file_name + '.' + file_extension
		
		with open(file_path + f"{file_with_extension}", "wb") as fh:
			fh.write(
				base64.decodebytes(
					b64_str.replace(replace, '').encode()
				)
			)
		return file_with_extension

	except Exception as e:
		raise e

def save_file_to_s3(path, b64_str, file_name, mobile, name):
	try:
		file_path = path + "\\"
		print(file_path)

		if 'jpg' or 'jpeg' in b64_str[:24]:
					file_extension = 'jpg'
					replace = 'data:image/jpeg;base64,'
				
		if 'png' in b64_str[:23]:
			file_extension = 'png'
			replace = 'data:image/png;base64,'

		file_with_extension = mobile + '_' + name.replace(' ', '_').lower() + '_' + file_name + '.' + file_extension
		file = file_path + f"{file_with_extension}"

		with open(file, "wb") as fh:
			fh.write(
				base64.decodebytes(
					b64_str.replace(replace, '').encode()
				)
			)

		# Get AWS Credentials:

		AWS_ACCESS_KEY_ID = c_app.config.get('AWS_ACCESS_KEY_ID')
		AWS_SECRET_ACCESS_KEY = c_app.config.get('AWS_SECRET_ACCESS_KEY')
		AWS_REGION = c_app.config.get('AWS_REGION')

		s3_client = boto3.client('s3', 
			aws_access_key_id=AWS_ACCESS_KEY_ID, 
			aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
			region_name=AWS_REGION
		)

		print(AWS_ACCESS_KEY_ID)
		print(AWS_SECRET_ACCESS_KEY)
		print(s3_client)

		# Upload File and Delete from Local Directory:

		with open(file, "rb") as f:
		    s3_client.upload_fileobj(f, "kiranevala", f"{file_with_extension}")

		time.sleep(5.0)
		os.remove(file)

		return file_with_extension

	except Exception as e:
		raise e