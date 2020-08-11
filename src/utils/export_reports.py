'''
'''

# Import Modules:

import pdfkit

# Class Definitions:

class Pdf:
    '''
    '''
    def __init__(self, filename):
        '''
        '''
        self.filename = filename
        self.file_path = file_path

    def parse_url(self, url):
        '''
        '''
        try:
            pdfkit.from_url(url, filename)
        except Expression as e:
            raise e

    def parse_file(self, file_path):
        '''
        '''
        try:
            pdfkit.from_url(filename)
        except Expression as e:
            raise e

    def parse_string(self, string):
        '''
        '''
        try:
            pdfkit.from_url(string, filename)
        except Expression as e:
            raise e
        