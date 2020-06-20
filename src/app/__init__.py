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
	from routes.user import Users
	from routes.test import TestQuestionDetails
	# from routes.ui import VendorUI

	api.add_resource(Welcome, '/edu/v1/welcome', methods=['GET'], endpoint='welcome_api')
	api.add_resource(Users, '/edu/v1/users/get-user', methods=['GET'], endpoint='get_user')
	api.add_resource(Users, '/edu/v1/users/add-user', methods=['POST'], endpoint='add_user')
	api.add_resource(Users, '/edu/v1/users/mod-user', methods=['PUT'], endpoint='mod_user')
	# api.add_resource(Vendor, '/edu/v1/vendor', methods=['GET'], endpoint='get_vendor')
	# api.add_resource(VendorUI, '/', methods=['GET'], endpoint='register_vendor')
	api.add_resource(TestQuestionDetails, '/edu/v1/test', methods=['POST'], endpoint='add_test')
	# api.add_resource(Vendor, '/edu/v1/vendor', methods=['PUT'], endpoint='mod_vendor')

	return app