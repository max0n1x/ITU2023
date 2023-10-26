from configparser import ConfigParser
import os

config = ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'))

DATABASE_FILE = config['database']['file']

ENDPOINT_HOST = config['endpoint']['host']
ENDPOINT_PORT = int(config['endpoint']['port'])