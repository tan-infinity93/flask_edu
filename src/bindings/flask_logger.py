'''
'''

# Import Modules:

import csv
import logging
from datetime import datetime, date
from flask import current_app as c_app
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.constants import constants

# Class Definition:

class FlaskLogger:

	def __init__(self, app=None, config_prefix="FLASK_LOGGER", **kwargs):
		'''
		'''
		self.config_prefix = config_prefix

		if app is not None:
			self.init_app(app)

	def init_app(self, app, **kwargs):
		'''
		'''
		try:
			app_env = app.config.get('ENV')
			logger = app.config.get('LOGGER_NAME')

			if app_env == 'development':
				APP_LOGS = logging.getLogger(logger.replace('.log', ''))
				APP_LOGS.setLevel(logging.DEBUG)
				FH = logging.FileHandler(logger)
				FH.setLevel(logging.DEBUG)
				CH = logging.StreamHandler()
				CH.setLevel(logging.ERROR)
				FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s: %(lineno)d - %(levelname)s - %(message)s')
				FH.setFormatter(FORMATTER)
				CH.setFormatter(FORMATTER)
				APP_LOGS.addHandler(FH)
				APP_LOGS.addHandler(CH)

			if app_env == 'production':
				kibana_host = app.config.get("KIBANA_HOST")
				kibana_port = app.config.get("KIBANA_PORT")
				APP_LOGS = logging.getLogger(logger.replace('.log', ''))
				APP_LOGS.setLevel(logging.INFO)
				APP_LOGS.addHandler(AsynchronousLogstashHandler(kibana_host, kibana_port, database_path=None))

			app.config['APP_LOGS'] = APP_LOGS

		except Exception as e:
			raise e

	@staticmethod
	def log(method_name, action, response, input_data=None, log_level=None):
		'''
		'''
		try:
			app_logger = c_app.config.get('APP_LOGS')
			log_dict = {
				'method_name': method_name,
				'action': action,
				'request': input_data,
				'response': response
			}

			if log_level == 'debug':
				app_logger.debug(log_dict)
			if log_level == 'info':
				app_logger.info(log_dict)
			if log_level == 'warning':
				app_logger.warning(log_dict)
			if log_level == 'error':
				app_logger.error(log_dict)
			if log_level == 'critical':
				app_logger.critical(log_dict)

		except Exception as e:
			raise e

	@staticmethod
	def writecsvlog(payload, exchange, queue, exception):
		'''
		'''
		try:
			path = c_app.config.get('RABBITMQ_ERROR_CSV_PATH')
			day = date.today()
			file = 'whatsapp_api_rabbitmq_log.csv'
			filepath = f'{path}/{day}_{file}'

			with open(filepath, 'a+') as csvFile:
				row = [payload, exchange, queue, exception]
				writer = csv.writer(csvFile)
				writer.writerow(row)

		except Exception as e:
			raise e