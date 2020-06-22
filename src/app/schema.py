'''
'''

# Import Modules:

from marshmallow import Schema, fields, validate
from marshmallow.validate import OneOf

# Schema Definitions:

class Token(Schema):
	'''
	'''
	username = fields.Str(required=True)
	password = fields.Str(required=True)

class Users(Schema):
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
		required=True,
		validate=[
			validate.Length(min=4), validate.Length(max=4)
		]
	)
	answer = fields.Str(required=True)

class TestQuestionDetails(TestDetails):
	'''
	'''
	qna = fields.List(
		fields.Nested(QuestionAnswer),
		required=True
	)