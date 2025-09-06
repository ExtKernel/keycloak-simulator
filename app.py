from sys import argv
from flask import Flask
from flask_caching import Cache
from utils import Logger, ConfigHandler
from user import UserAPI
from auth import AuthAPI

app = Flask(__name__)
logger = Logger('flask')
logger = logger.get_logger('werkzeug')
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

if __name__ == "__main__":
    try:
        config = argv[1]
    except IndexError:
        logger.error('Please specify a config file as a first positional argument.')
        exit(1)

    config_handler = ConfigHandler()
    # Initialize user-related endpoints
    user_api = UserAPI(
        cache,
        config_handler.get_config('USER', config)
    )
    user_api.init_admin()
    user_api.init_endpoints(app)

    # Initialize OAuth2-related endpoints
    auth_api = AuthAPI(
        cache,
        config_handler.get_config('AUTH', config),
        user_api.get_admin()
    )
    auth_api.init_endpoints(app)

    app.run(host='0.0.0.0')
