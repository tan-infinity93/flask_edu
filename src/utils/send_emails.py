'''
'''

# Import Modules:

import smtplib
from flask import current_app as c_app

# Class Definitions:

class Gmailer:
	'''
	'''
	def __init__(self):
		self.smtp_server = c_app.config.get('SMTP_SERVER')
		self.smtp_port = c_app.config.get('SMTP_PORT')
		self.smtp_session = smtplib.SMTP(self.smtp_server, self.smtp_port)
		self.smtp_email_id = c_app.config.get('SMTP_EMAIL_ID')
		self.smtp_email_password = c_app.config.get('SMTP_EMAIL_PASSWORD')

	def send_mail(self, receiver_email_id, email_message):
		'''
		'''
		try:
			self.smtp_session.starttls()
			self.smtp_session.login(self.smtp_email_id, self.smtp_email_password) 
			self.smtp_session.sendmail(self.smtp_email_id, receiver_email_id, email_message) 
			self.smtp_session.quit()

		except Exception as e:
			raise e
