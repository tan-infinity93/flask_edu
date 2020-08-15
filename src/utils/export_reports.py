'''
'''

# Import Modules:

import os
import pdfkit
from flask import current_app as c_app

# Class Definitions:

class PdfGenerator:
    '''
    '''
    def __init__(self, file_name):
        '''
        '''
        self.file_name = file_name
        self.files_dir = c_app.config.get('FILES_DIR')
        self.check_directory_path()

    def check_directory_path(self):
        '''
            Check if DIR exists else create new DIR at Path
        '''
        try:
            if not os.path.isdir(self.files_dir):
                os.makedirs(self.files_dir)

        except Exception as e:
            raise e

    def parse_url(self, url):
        '''
        '''
        try:
            pdf_path = f'{self.files_dir}/{self.file_name}'
            pdfkit.from_url(url, pdf_path)

        except Exception as e:
            raise e

    def parse_file(self, file_path):
        '''
        '''
        try:
            pdf_path = f'{self.files_dir}/{self.file_name}'
            pdfkit.from_file(pdf_path)

        except Exception as e:
            raise e

    def parse_string(self, string):
        '''
        '''
        try:
            pdf_path = f'{self.files_dir}/{self.file_name}'
            pdfkit.from_string(string, pdf_path)

        except Exception as e:
            raise e
        