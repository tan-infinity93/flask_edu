'''
'''

# Import Modules:

from marshmallow import (
	Schema, fields, validate, validates_schema, ValidationError
)
from marshmallow.validate import OneOf
from dateutil.parser import parse

# Schema Definitions:

class Token(Schema):
	'''
	'''
	username = fields.Str(required=True)
	password = fields.Str(required=True)

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
	email_id = fields.Str(required=True)
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

class StudentUsers(Schema):
	'''
	'''
	

class TestDetails(Schema):
	'''
	'''
	customerid = fields.Str(required=True)
	testid = fields.Str(required=False)
	details = fields.Str(required=True)
	schedule = fields.DateTime(required=True)
	duration = fields.Float(required=True)
	created = fields.DateTime(required=True)
	start_time = fields.DateTime(required=True)
	end_time = fields.DateTime(required=True)
	no_mandatory_questions = fields.Integer(required=True, strict=True)

class QuestionAnswer(Schema):
	'''
	'''
	_id = fields.Str(required=False)
	question = fields.Str(required=True)
	options = fields.List(
		fields.Str(),
		required=False,
		validate=[
			validate.Length(min=4), validate.Length(max=4)
		]
	)
	answer = fields.Str(required=True)
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
		end_time = data.get('end_time')
		# end_time = parse(end_time)
		duration = data.get('duration')
		duration = duration * 60

		if schedule_time > end_time:
			print(end_time - schedule_time)
			raise ValidationError('end time cannot be less than scheduled time')
		elif end_time > schedule_time:
			time_delta = (end_time - schedule_time).total_seconds()/60
			print(time_delta)
			print(type(time_delta))
			if duration < (time_delta):
				raise ValidationError('duration and time delta do not match')

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