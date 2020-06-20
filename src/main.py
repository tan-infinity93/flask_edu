'''
    This module import the Flask App instance created via the App
    Factory Pattern and runs the application
'''

# Import Modules:

import os
from flask import Flask
from app import create_app

# Get App Instance:

config_name = os.getenv('ENV', 'development')
app = create_app(config_name)

# Run App:

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config.get('PORT'), debug=app.config.get('DEBUG'))