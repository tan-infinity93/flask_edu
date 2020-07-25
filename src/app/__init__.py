'''
'''

# Import Modules:

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from config import get_config

# Create Flask App Factory:

def create_app(config_name):
	app = Flask(__name__, template_folder='../templates/',  static_folder='../static')
	CORS(app)
	app.config.update(get_config(config_name))

	# App Binding:

	from bindings.flask_mongo import FlaskMongo

	mongo_app = FlaskMongo()
	mongo_app.init_app(app)

	api = Api(app, catch_all_404s=True)
	# api = Api()

	# print(app.config.keys())

	# Add API Routes:

	from routes.welcome import Welcome
	from routes.auth import Auth
	from routes.teacher import TeacherUsers
	from routes.student import StudentUsers
	from routes.test import TestQuestionDetails
	# from routes.ui import VendorUI

	api.add_resource(Welcome, '/edu/v1/api/welcome', methods=['GET'], endpoint='welcome_api')

	api.add_resource(Auth, '/edu/v1/api/generate-token', methods=['POST'], endpoint='generate_token')
	
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/get-user', methods=['GET'], endpoint='get_tuser')
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/add-user', methods=['POST'], endpoint='add_tuser')
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/mod-user', methods=['PUT'], endpoint='mod_tuser')

	api.add_resource(StudentUsers, '/edu/v1/users/student/get-user', methods=['GET'], endpoint='get_suser')
	api.add_resource(StudentUsers, '/edu/v1/users/student/add-user', methods=['POST'], endpoint='add_suser')
	api.add_resource(StudentUsers, '/edu/v1/users/student/mod-user', methods=['PUT'], endpoint='mod_suser')

	# api.add_resource(Vendor, '/edu/v1/vendor', methods=['GET'], endpoint='get_vendor')
	# api.add_resource(VendorUI, '/', methods=['GET'], endpoint='register_vendor')
	api.add_resource(TestQuestionDetails, '/edu/v1/tests/get-test', methods=['GET'], endpoint='get_test')
	api.add_resource(TestQuestionDetails, '/edu/v1/tests/create-test', methods=['POST'], endpoint='add_test')
	api.add_resource(TestQuestionDetails, '/edu/v1/tests/mod-test', methods=['PUT'], endpoint='mod_test')

	return app