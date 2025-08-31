from sys import argv
from flask import Flask
from utils import Logger, get_config
from user import UserAPI

app = Flask(__name__)
logger = Logger('flask')
logger = logger.get_logger('werkzeug')

if __name__ == "__main__":
    try:
        config = argv[1]
    except IndexError:
        logger.error('Please specify a config file as a first positional argument.')
        exit(1)
    user_api = UserAPI(get_config(config))
    user_api.init_endpoints(app)

    app.run()
