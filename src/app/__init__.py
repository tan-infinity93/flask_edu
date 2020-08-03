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
	from routes.subscription import ResetTrial
	from routes.teacher import TeacherUsers
	from routes.student import StudentUsers
	from routes.test import TestQuestionDetails
	from routes.testattempt import TestAttemptDetails, TestAttemptComplete
	from routes.stats import TestScoresStats, StudentsStats
	from routes.rooms import RoomsApi
	from routes.rooms_enrolled import RoomsEnrolled

	api.add_resource(Welcome, '/edu/v1/api/welcome', methods=['GET'], endpoint='welcome_api')

	api.add_resource(Auth, '/edu/v1/api/generate-token', methods=['POST'], endpoint='generate_token')

	api.add_resource(ResetTrial, '/edu/v1/users/reset-trial', methods=['POST'], endpoint='reset_trial')
	
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/get-user', methods=['GET'], endpoint='get_tuser')
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/add-user', methods=['POST'], endpoint='add_tuser')
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/mod-user', methods=['PUT'], endpoint='mod_tuser')
	api.add_resource(TeacherUsers, '/edu/v1/users/teacher/del-user', methods=['DELETE'], endpoint='del_tuser')

	api.add_resource(StudentUsers, '/edu/v1/users/student/get-user', methods=['GET'], endpoint='get_suser')
	api.add_resource(StudentUsers, '/edu/v1/users/student/add-user', methods=['POST'], endpoint='add_suser')
	api.add_resource(StudentUsers, '/edu/v1/users/student/mod-user', methods=['PUT'], endpoint='mod_suser')
	api.add_resource(TeacherUsers, '/edu/v1/users/student/del-user', methods=['DELETE'], endpoint='del_suser')

	api.add_resource(TestQuestionDetails, '/edu/v1/tests/get-test', methods=['GET'], endpoint='get_test')
	api.add_resource(TestQuestionDetails, '/edu/v1/tests/create-test', methods=['POST'], endpoint='add_test')
	api.add_resource(TestQuestionDetails, '/edu/v1/tests/mod-test', methods=['PUT'], endpoint='mod_test')

	api.add_resource(TestAttemptDetails, '/edu/v1/testattempts/create-test', methods=['POST'], endpoint='create_testa')
	api.add_resource(TestAttemptDetails, '/edu/v1/testattempts/mod-test', methods=['PUT'], endpoint='mod_testa')

	api.add_resource(TestAttemptComplete, '/edu/v1/testcomplete/mod-test', methods=['PUT'], endpoint='mod_testc')

	api.add_resource(TestScoresStats, '/edu/v1/teststats/get-test', methods=['GET'], endpoint='get_test_stats')
	api.add_resource(StudentsStats, '/edu/v1/studentstats/get-test', methods=['GET'], endpoint='get_stu_stats')
	
	api.add_resource(RoomsApi, '/edu/v1/rooms/create-room', methods=['POST'], endpoint='add_room')
	api.add_resource(RoomsApi, '/edu/v1/rooms/get-room', methods=['GET'], endpoint='get_room')
	api.add_resource(RoomsApi, '/edu/v1/rooms/mod-room', methods=['PUT'], endpoint='mod_room')
	api.add_resource(RoomsApi, '/edu/v1/rooms/del-room', methods=['DELETE'], endpoint='del_room')

	api.add_resource(RoomsEnrolled, '/edu/v1/rooms/create-room-enroll', methods=['POST'], endpoint='add_room_enroll')
	api.add_resource(RoomsEnrolled, '/edu/v1/rooms/get-room-enroll', methods=['GET'], endpoint='get_room_enroll')
	api.add_resource(RoomsEnrolled, '/edu/v1/rooms/mod-room-enroll', methods=['PUT'], endpoint='mod_room_enroll')
	api.add_resource(RoomsEnrolled, '/edu/v1/rooms/del-room-enroll', methods=['DELETE'], endpoint='del_room_enroll')

	return app
