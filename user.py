import json

from uuid import uuid4
from datetime import datetime
from flask import request, jsonify
from utils import Logger

logger = Logger('user')
logger = logger.get_logger()


def cache_user(user, cache):
    cached_users = cache.get('users')
    cached_users.append(user)

    cache.delete('users')
    cache.add('users', cached_users)

def get_cached_user(user_id, cache):
    cached_users = cache.get('users')

    for user in cached_users:
        if str(user.id) == user_id:
            return user
    raise KeyError(f'User with id {user_id} not found')

class User:
    def __init__ (self, *args, **kwargs):
        self.id = uuid4()
        self.createdTimestamp = int(datetime.now().timestamp() * 1000) # * 1000 - microseconds to milliseconds

        # Minimal required args to build a Keycloak user
        required_args = ['username', 'enabled', 'firstName', 'lastName', 'email']

        # If no dict representation of a user was passed
        # Try to build it from individual args passed
        # Exception if neither worked
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
    def __init__ (self, cache, config):
        self.cache = cache
        if cache.get('users') is None:
            cache.add('users', [])
        # Set config entries as attributes
        for k, v in config.items():
            setattr(self, k, v)

    def validate_realm(self, request_realm):
        if request_realm != self.realm:
            message = f'Invalid realm. \"{request_realm}\" does not reflect the configured realm'
            logger.error(message)
            raise ValueError(message)
        return True

    def init_error_handlers(self, app):
        """
        Master function for initializing error handlers.
        Supposed to be called before of initialization of endpoints
        or be included in its logic.

        :param app: flask app.
        :return: depends on the exception.
        """

        @app.errorhandler(Exception)
        def handle_exception(exception):
            app.logger.error(exception, exc_info=True)

            return jsonify({
                'exception': type(exception).__name__,
                'message': str(exception)
            }), 400

        @app.errorhandler(KeyError)
        def handle_keyerror(exception):
            app.logger.error(exception, exc_info=True)

            return jsonify({
                'exception': type(exception).__name__,
                'message': str(exception)
            }), 404

    def init_endpoints(self, app):
        """
        Master function for initializing user-related endpoints.

        :param app: flask app.
        :return: depends on the endpoint.
        """
        self.init_error_handlers(app)

        @app.route(self.create_user_endpoint, methods=['POST'])
        def create_user(realm):
            self.validate_realm(realm)
            # Try to build a user. If cannot, then request args are invalid
            try:
                user = User(user_dict=dict(request.json))
                cache_user(user, self.cache)
            except ValueError as exception:
                return jsonify({
                    'error': 'invalid_request',
                    'error_description': str(exception)
                }), 400
            return '', 201

        @app.route(self.get_user_endpoint, methods=['GET'])
        def get_user(realm, user_id):
            self.validate_realm(realm)

            user = get_cached_user(user_id, self.cache)

            template = json.loads(open(self.get_user_response_template).read())
            template['id'] = user.id
            template['username'] = user.username
            template['firstName'] = user.firstName
            template['lastName'] = user.lastName
            template['email'] = user.email
            template['createdTimestamp'] = user.createdTimestamp
            template['enabled'] = user.enabled

            return jsonify(template)

        @app.route(self.get_users_endpoint, methods=['GET'])
        def get_users(realm):
            self.validate_realm(realm)

            return jsonify([user.__dict__ for user in self.cache.get('users')])

        @app.route(self.reset_user_password_endpoint, methods=['PUT'])
        def reset_password(realm, user_id):
            return f'{user_id} User\'s password reset!'

        @app.route(self.delete_user_endpoint, methods=['DELETE'])
        def delete_user(realm, user_id):
            self.validate_realm(realm)
            return f'{user_id} User deleted!'

