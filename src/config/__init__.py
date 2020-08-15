'''
'''

# Import Modules:

import os
import json

# App Config:

def get_config(config_names):
    """
    This method load multiple configurations if required. Pass configuration names
    separated by space or comma

        get_config('development') --> loads configuration from development.json file
        get_config('development production') -->
            loads configuration from development.json file and override these
            configurations from production.json file

    NOTE:
    Configuration json files are in gitignore to avoid configuration data in VCR.
    Use .example files to share the format or example of configuration files.
    """

    configs = config_names.split()
    config_data = dict()

    for config_name in configs:
        # print("loading configurations from {}.json file...".format(config_name))
        config_file = ".".join([config_name.lower(), "json"])
        config_file_path = os.path.join(os.path.dirname(__file__), config_file)

        if not os.path.exists(config_file_path):
            raise FileNotFoundError("{}.json configuration file do not exist in `config` directory.".format(config_name))

        with open(config_file_path) as file:
            config_data.update(json.loads(file.read()))

    # Update Account Scopes:

    teacher_scope = config_data.get('SCOPES').get('teacher')
    student_scope = config_data.get('SCOPES').get('student')
    admin_scope = config_data.get('SCOPES').get('admin')
    admin_scope = list(set(admin_scope + teacher_scope + student_scope))
    config_data['SCOPES']['admin'] = admin_scope

    return config_data