from configparser import RawConfigParser
from copy import copy
import os
from datetime import datetime

now = datetime.now().strftime('%Y%m%d_%H%M')

SECTION_DEFAULTS = {
    'log_stream_name': now + '_{hostname}',
    'time_zone': 'UTC',
    'initial_position': 'start_of_file',
}


class ConfigFile(object):

    def __init__(self, config_path, state_path):
        self.ini = RawConfigParser()
        self.config_path = config_path
        self.state_path = state_path

    def add_section(self, section, options):
        self.ini.add_section(section)
        for k, v in options.items():
            self.ini.set(section, k, v)

    def autoconfigure(self):
        options = extract_section_options_from_env('CWLOGS')
        options.update({'state_file': self.state_path})
        self.add_section('general', options)
        for section in extract_sections_from_env():
            self.add_log_section(*section)

    def add_log_section(self, section, raw_options):
        options = copy(SECTION_DEFAULTS)
        options.update(raw_options)
        self.add_section(section, options)

    def write(self):
        with open(self.config_path, 'w') as fh:
            self.ini.write(fh)


def section_name_is_valid(section_name):
    required_vars = ('LOG_GROUP_NAME', 'FILE')
    for required_var in required_vars:
        required_var = '{}_{}'.format(section_name, required_var)
        if not os.environ.get(required_var):
            return False
    return True


def extract_section_options_from_env(section_name):
    options = {}
    prefix = section_name + '_'
    for k, v in os.environ.items():
        if not k.startswith(section_name + '_'):
            continue
        option_name = k[len(prefix):].lower()
        options[option_name] = v
    return options


def extract_sections_from_env():
    find_suffix = '_LOG_GROUP_NAME'
    valid_section_names = []
    for env_var in os.environ.keys():
        if not env_var.endswith(find_suffix):
            continue
        section_name = env_var[0:-len(find_suffix)]
        if not section_name_is_valid(section_name):
            continue
        valid_section_names.append(section_name)

    return (
        (section_name.lower(), extract_section_options_from_env(section_name))
        for section_name in valid_section_names
    )
