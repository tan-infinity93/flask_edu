'''
'''

# Import Modules:

from datetime import datetime
from marshmallow import (
	Schema, fields, validate, validates, validates_schema, ValidationError
)
from marshmallow.validate import OneOf
from dateutil.parser import parse
import bson

# Schema Definitions:

class Token(Schema):
	'''
	'''
	username = fields.Str(required=True)
	password = fields.Str(required=True)

class ResetTrial(Schema):
	'''
	'''
	userid = fields.Str(required=False)
	no_free_trial = fields.Integer(required=False, strict=True)

	@validates('userid')
	def check_mongo_objectid(self, value):
		'''
		'''
		is_valid = bson.objectid.ObjectId.is_valid(value)
		if not is_valid:
			# error = {'id error': 'please check userid, is invalid'}
			error = 'please check userid, is invalid'
			raise ValidationError(error)

class Pdf(Schema):
	'''
	'''
	file_name = fields.Str(required=True, validate=[validate.Length(min=5)])
	url = fields.Url(required=False, schemes=['http', 'https'])
	file_path = fields.Str(required=False)
	string = fields.Str(required=False)

class Email(Schema):
	'''
	'''
	receiver_email_id = fields.Email(required=True)
	email_message = fields.Str(required=True, validate=[validate.Length(min=10)])


class TeacherUsers(Schema):
	'''
	'''
	valid_institute_types = ['school', 'jr.college', 'degree college']
	
	name = fields.Str(required=True)
	institute_name = fields.Str(required=True)
	institute_type = fields.Str(
		required=True,
		validate = [
			OneOf(valid_institute_types)
		]
	)
	phone_no = fields.Str(required=True)
	email_id = fields.Email(required=True)
	username = fields.Str(required=True)
	password = fields.Str(required=True)
	no_free_trial = fields.Integer(required=False, strict=True)
	is_active = fields.Boolean(
		required=False,
		default=True,
		validate=[
			OneOf([True, False])
		]
	)
	userid = fields.Str(required=False)

	@validates('userid')
	def check_mongo_objectid(self, value):
		'''
		'''
		is_valid = bson.objectid.ObjectId.is_valid(value)
		if not is_valid:
			error = {'id error': 'please check userid, is invalid'}
			raise ValidationError(error)

class StudentUsers(Schema):
	'''
	'''

class TestDetails(Schema):
	'''
	'''
	customerid = fields.Str(required=True, validate=[validate.Length(min=24)])
	testid = fields.Str(required=False, validate=[validate.Length(min=32)])
	details = fields.Str(required=True, validate=[validate.Length(min=10)])
	schedule = fields.DateTime(required=True)
	duration = fields.Float(required=True, validate=[validate.Range(min=0.5, max=3.0)])
	# created = fields.DateTime(required=True)
	start_time = fields.DateTime(required=True)
	end_time = fields.DateTime(required=True)
	no_mandatory_questions = fields.Integer(required=True, strict=True, validate=[validate.Range(min=1, max=10)])

class QuestionAnswer(Schema):
	'''
		Issue: validator not working in nested
	'''
	_id = fields.Str(required=False)
	question = fields.Str(required=True, validate=[validate.Length(min=3)])
	options = fields.List(
		fields.Str(),
		required=False,
		validate=[
			validate.Length(min=4), validate.Length(max=4)
		]
	)
	answer = fields.Str(required=True, validate=[validate.Length(min=1)])
	is_correct = fields.Boolean(required=False)

class TestQuestionDetails(TestDetails):
	'''
	'''
	qna = fields.List(
		fields.Nested(QuestionAnswer),
		required=True
	)

	@validates_schema
	def check_qna_count(self, data, **kwargs):
		'''
		'''
		print(f'data: {data}\n')

		count_qna = data.get('no_mandatory_questions')
		actual_count_qna = len(data.get('qna'))

		if actual_count_qna < count_qna:
			raise ValidationError('list of questions not equal to no of provided count')
		
		schedule_time = data.get('schedule')
		# schedule_time = parse(schedule_time)
		current_time = datetime.now()
		start_time = data.get('start_time')
		end_time = data.get('end_time')
		# end_time = parse(end_time)
		duration = data.get('duration')
		duration = duration * 60

		if schedule_time < current_time:
			raise ValidationError('test cannot be created/modified for previous datetime')

		elif schedule_time > end_time:
			print(end_time - schedule_time)
			raise ValidationError('end time cannot be less than scheduled time')

		elif start_time < schedule_time:
			error = {'time error': 'start time cannot be less than scheduled time'}
			raise ValidationError(error)

		elif end_time > schedule_time:
			time_delta = (end_time - start_time).total_seconds()/60
			print(f'time_delta: {time_delta}')
			print(type(time_delta))
			print(f'duration: {duration}')
			if duration < (time_delta):
				error = {'difference': 'duration and time delta do not match, should be equal'}
				raise ValidationError(error)

class TestDeletion(Schema):
	'''
	'''
	test_id = fields.Str(required=True)

class TestAttempt(Schema):
	'''
	'''
	student_id = fields.Str(required=True)
	test_id = fields.Str(required=True)
	student_name = fields.Str(required=True)
	phone_no = fields.Str(required=True)
	qna = fields.List(
		fields.Nested(QuestionAnswer),
		required=True
	)
	is_complete = fields.Boolean(required=False)
	deleted = fields.Integer(required=False, strict=True)

	@validates('student_id')
	def check_mongo_objectid(self, value):
		'''
		'''
		is_valid = bson.objectid.ObjectId.is_valid(value)
		if not is_valid:
			error = {'id error': 'please check student_id, is invalid'}
			raise ValidationError(error)

class Rooms(Schema):
	'''
	'''
	teacher_id = fields.Str(required=True)
	room_id = fields.Str(required=False)
	limit = fields.Integer(required=True, strict=True)
	agenda = fields.Str(required=True)
	room_name = fields.Str(required=True)
	deleted = fields.Boolean(required=False)

	@validates('teacher_id')
	def check_mongo_objectid(self, value):
		'''
		'''
		is_valid = bson.objectid.ObjectId.is_valid(value)
		if not is_valid:
			raise ValidationError('please check teacher_id, is invalid')

class RoomsEnrolled(Schema):
	'''
	'''
	teacher_id = fields.Str(required=True)
	room_id = fields.Str(required=False)
	student_id = fields.Str(required=True)
	reason = fields.Str(required=False)
	banned = fields.Boolean(required=False)
	deleted = fields.Boolean(required=False)

	@validates('student_id')
	def check_mongo_objectid(self, value):
		'''
		'''
		is_valid = bson.objectid.ObjectId.is_valid(value)
		if not is_valid:
			raise ValidationError('please check student_id, is invalid')