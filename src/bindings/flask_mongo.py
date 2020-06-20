'''
'''

# Import Modules:

import uuid
from datetime import datetime
import pymongo
from flask import current_app as c_app
from collections.abc import Iterable
# from utils.common_functions import convertbase64tomd5

# Class Definitions:

class FlaskMongo:
	'''
	'''
	def __init__(self, app=None, **kwargs):
		'''
		'''
		self.uri = None
		self.database = None
		self.app = app

		if self.app is not None:
			self.init_app(self.app)

	def init_app(self, app, **kwargs):
		'''
		'''
		self.uri = app.config.get('MONGO_URL')
		self.database = app.config.get('MONGO_DATABASE')
		self.mongo_connection = pymongo.MongoClient(self.uri)
		self.mongo_database = self.mongo_connection[self.database]
		app.config['MONGO_CONNECTION'] = self.mongo_connection
		app.config['MONGO_DATABASE'] = self.mongo_database

	@staticmethod
	def insert(db, collection, data):
		'''
		'''
		try:
			db = c_app.config.get('MONGO_DATABASE')
			col = db[collection]
			col.insert_one(data)

		except Exception as e:
			raise e

	@staticmethod
	def find(collection, columns, **queries):
		'''
		'''
		try:
			db = c_app.config.get('MONGO_DATABASE')
			col = db[collection]
			data = col.find(queries, columns)

			print(f'queries: {queries}')
			print(f'columns: {columns}')
			print(f'collection: {collection}')
			# print(f'data: {list(data)}')

			print(type(data))

			# if queries == {}:
			# 	data = col.find(queries, columns)
			# else:
			# 	data = col.find_one(queries, columns)
			# return list(data)

			if isinstance(data, pymongo.cursor.Cursor):
			# 	print('if')
			# 	print(list(data))
				return [d for d in data]
			# 	# return list(data)
			else:
				print('else')
				return data

		except Exception as e:
			raise e


	@staticmethod
	def update(collection, updates, **queries):
		'''
		'''
		try:
			db = c_app.config.get('MONGO_DATABASE')
			col = db[collection]
			col.update(
				queries,
				{
					'$set': updates
				}
			)

		except Exception as e:
			raise e