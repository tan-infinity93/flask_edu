'''
'''

# Import Modules:

import json
import uuid
from datetime import datetime

from app.schema import TestQuestionDetails
from bindings.flask_mongo import FlaskMongo
from bson.objectid import ObjectId
from flask import Flask
from flask import current_app as c_app
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from middleware.decorators import is_valid_args, is_valid_json
from utils.common_functions import format_api_error

# Class Definitions:

class TestScoresStats(Resource):
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
        self.no_data_code = 404
        self.process_error_code = 422
        self.exception_code = 500

    @is_valid_args
    def get(self):
        '''
        '''
        try:
            args_data = request.args.to_dict()
            test_id = args_data.get('testid')

            collection1 = 'common_test_student_ques_answers'
            collection2 = 'common_test_master'

            columns = {'_id': 0}
            queries1 = {'test_id': test_id}
            query_data1 = FlaskMongo.find(collection1, columns, queries1)

            queries2 = {'id': test_id}
            query_data2 = FlaskMongo.find(collection2, columns, queries2)

            if query_data1 and query_data2:
                query_data2 = query_data2[0]
                print(query_data2)

                # query_data1 = query_data1[0]
                # print(query_data1)

                stats = {
                    'total': query_data2.get('no_mandatory_questions'),
                    'correct': 0,
                    'incorrect': 0,
                    'score': 0
                }

                for qd in query_data1:
                    if qd.get('is_correct'):
                        stats['correct'] = stats['correct'] + 1
                stats['incorrect'] = stats['total'] - stats['correct']
                stats['score'] = str(round(stats['correct']/stats['total'] * 100, 2)) + '%'

                response = {
                    "meta": self.meta,
                    # "message": f"no data found for test id {test_id}",
                    "status": "success",
                    "stats": stats
                }
                return response, self.success_code, self.headers

            else:
                response = {
                    "meta": self.meta,
                    "message": f"no data found for test id {test_id}",
                    "status": "failure"
                }
                return response, self.no_data_code, self.headers

        except Exception as e:
            # raise e
            response = {
                "meta": self.meta,
                "message": "unable to process request",
                "status": "failure",
                "reason": str(e)
            }
            return response, self.exception_code, self.headers


class StudentsStats(Resource):
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
        self.no_data_code = 404
        self.process_error_code = 422
        self.exception_code = 500

    @is_valid_args
    def get(self):
        '''
        '''
        try:
            args_data = request.args.to_dict()

            print(args_data)

            student_id = args_data.get('studentid')

            collection1 = 'common_test_student'
            # collection2 = 'common_test_master'

            columns = {'_id': 0, "test_id": 1, "is_complete": 1}
            queries1 = {'student_id': student_id}
            query_data1 = FlaskMongo.find(collection1, columns, queries1)

            # queries2 = {'id': student_id}
            # query_data2 = FlaskMongo.find(collection2, columns, queries2)

            if query_data1:
                # query_data1 = query_data1[0]
                print(f'query_data1: {query_data1}')

                # query_data1 = query_data1[0]
                # print(query_data1)

                stats = {
                    'total': len(query_data1),
                    'complete': 0,
                    'incomplete': 0,
                    'test-ids': []
                }

                for qd in query_data1:
                    if qd.get('is_complete'):
                        stats['complete'] = stats['complete'] + 1
                    stats['test-ids'].append(qd.get('test_id'))

                stats['incomplete'] = stats['total'] - stats['complete']
                

                response = {
                    "meta": self.meta,
                    # "message": f"no data found for test id {student_id}",
                    "status": "success",
                    "stats": stats
                }
                return response, self.success_code, self.headers

            else:
                response = {
                    "meta": self.meta,
                    "message": f"no data found for student with id {student_id}",
                    "status": "failure"
                }
                return response, self.no_data_code, self.headers

        except Exception as e:
            # raise e
            response = {
                "meta": self.meta,
                "message": "unable to process request",
                "status": "failure",
                "reason": str(e)
            }
            return response, self.exception_code, self.headers

class RoomsStats(Resource):
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
        self.no_data_code = 404
        self.process_error_code = 422
        self.exception_code = 500

    @is_valid_args
    def get(self):
        '''
        '''
        try:
            args_data = request.args.to_dict()

            print(args_data)

            student_id = args_data.get('studentid')

            collection1 = 'common_test_student'
            # collection2 = 'common_test_master'

            columns = {'_id': 0, "test_id": 1, "is_complete": 1}
            queries1 = {'student_id': student_id}
            query_data1 = FlaskMongo.find(collection1, columns, queries1)

            # queries2 = {'id': student_id}
            # query_data2 = FlaskMongo.find(collection2, columns, queries2)

            if query_data1:
                # query_data1 = query_data1[0]
                print(f'query_data1: {query_data1}')

                # query_data1 = query_data1[0]
                # print(query_data1)

                stats = {
                    'total': len(query_data1),
                    'complete': 0,
                    'incomplete': 0,
                    'test-ids': []
                }

                for qd in query_data1:
                    if qd.get('is_complete'):
                        stats['complete'] = stats['complete'] + 1
                    stats['test-ids'].append(qd.get('test_id'))

                stats['incomplete'] = stats['total'] - stats['complete']
                

                response = {
                    "meta": self.meta,
                    # "message": f"no data found for test id {student_id}",
                    "status": "success",
                    "stats": stats
                }
                return response, self.success_code, self.headers

            else:
                response = {
                    "meta": self.meta,
                    "message": f"no data found for student with id {student_id}",
                    "status": "failure"
                }
                return response, self.no_data_code, self.headers

        except Exception as e:
            # raise e
            response = {
                "meta": self.meta,
                "message": "unable to process request",
                "status": "failure",
                "reason": str(e)
            }
            return response, self.exception_code, self.headers