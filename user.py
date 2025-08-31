from flask import request, jsonify
from utils import Logger, get_config

logger = Logger('user')
logger = logger.get_logger()


class User:
    def __init__ (self, *args, **kwargs):
        required_args = ['username', 'enabled', 'firstname', 'lastname', 'email']

        user_dict=None
        if 'user_dict' in kwargs:
            user_dict = kwargs['user_dict']
        if set(required_args).issubset(set(user_dict.keys())):
            for k, v in user_dict.items():
                setattr(self, k, v)
        elif required_args in args:
            for arg in required_args:
                setattr(self, arg, args.index(arg))
        else:
            message = ('User object is missing required arguments.'
                       ' Valid arguments were not given nor was a valid dict representation.')
            logger.error(message)
            raise ValueError(message)

    def check_credentials(self):
        credentials_fields = ['value', 'temporary']
        return True if set(self.credentials.keys()) == set(credentials_fields) else False


class UserAPI:
    def __init__ (self, config):
        for k, v in config.items():
            setattr(self, k, v)

    def validate_realm(self, request_realm):
        if request_realm != self.realm:
            message = f'Invalid realm. \"{request_realm}\" does not reflect the configured realm'
            logger.error(message)
            raise ValueError(message)
        return True

    def init_error_handlers(self, app):
        @app.errorhandler(Exception)
        def handle_exception(exception):
            app.logger.error(exception, exc_info=True)

            return jsonify({
                'exception': type(exception).__name__,
                'message': str(exception)
            }), 400

    def init_endpoints(self, app):
        self.init_error_handlers(app)

        @app.route(self.create_user_endpoint, methods=['POST'])
        def create_user(realm):
            self.validate_realm(realm)
            # Try to build a user. If cannot, then request args are invalid
            try:
                user = User(user_dict=dict(request.json))
            except ValueError as exception:
                return jsonify({'message': str(exception)}), 400
            return jsonify(user.__dict__)

        @app.route(self.get_user_endpoint, methods=['GET'])
        def get_user(realm, id):
            self.validate_realm(realm)
            return f'Here is {id} User!'

        @app.route(self.get_users_endpoint, methods=['GET'])
        def get_users(realm):
            self.validate_realm(realm)
            return 'Here are Users!'

        @app.route(self.reset_user_password_endpoint, methods=['PUT'])
        def reset_password(realm, id):
            return f'{id} User\'s password reset!'

        @app.route(self.delete_user_endpoint, methods=['DELETE'])
        def delete_user(realm, id):
            self.validate_realm(realm)
            return f'{id} User deleted!'

