import json

from uuid import uuid4
from flask import request, jsonify
from utils import (
    Logger,
    ConfigHandler,
    UserCacheHandler,
    get_epoch_mil_timestamp
)
from exception.exceptions import InvalidRealm, NoAdminUser

logger = Logger('user')
logger = logger.get_logger()


class User:
    def __init__ (self, **kwargs):
        self.id = uuid4()
        self.createdTimestamp = get_epoch_mil_timestamp()
        # Minimal required args to build a Keycloak user
        required_args = ['username', 'firstName', 'lastName', 'email', 'enabled']
        logger.info(f'Initializing a user\n'
                    f'Required arguments: {required_args}\n'
                    f'UID: {self.id}\nUNIX timestamp: {self.createdTimestamp}')

        # If no dict representation of a user was passed
        # Try to build it from individual args passed
        # Exception if neither worked
        if 'user_dict' in kwargs:
            user_dict = kwargs['user_dict']
            if set(required_args).issubset(set(user_dict.keys())):
                for k, v in user_dict.items():
                    setattr(self, k, v)
                    logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')
        elif set(required_args).issubset(set(kwargs)):
            for k, v in kwargs.items():
                setattr(self, k, v)
                logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')
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
        self.config_handler = ConfigHandler()
        self.cache_handler = UserCacheHandler(cache)
        # Set config entries as attributes
        for k, v in config.items():
            setattr(self, k, v)
            logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')

    def validate_realm(self, request_realm):
        if request_realm != self.realm:
            message = f'Invalid realm. \"{request_realm}\" does not reflect the configured realm'
            logger.error(message)
            raise InvalidRealm(message)
        return True

    def init_admin(self):
        template = self.config_handler.get_template(self.admin_user_template)
        self.cache_handler.cache_user(User(user_dict=template))

    def get_admin(self):
        template = self.config_handler.get_template(self.admin_user_template)
        template_admin_username = template['username']
        for user in self.cache_handler.get_cached_users():
            if user.username == template_admin_username:
                return user
            else:
                message = (f'No Keycloak admin user with template-matching username '
                           f'\"{template_admin_username}\" was initialized and/or cached')
                logger.error(message)
                raise NoAdminUser(message)


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
                self.cache_handler.cache_user(user)
            except ValueError as exception:
                return jsonify({
                    'error': 'invalid_request',
                    'error_description': str(exception)
                }), 400
            return '', 201

        @app.route(self.get_user_endpoint, methods=['GET'])
        def get_user(realm, user_id):
            self.validate_realm(realm)

            user = self.cache_handler.get_cached_user(user_id)

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

            return jsonify([user.__dict__ for user in self.cache_handler.get_cached_users()])

        @app.route(self.reset_user_password_endpoint, methods=['PUT'])
        def reset_password(realm, user_id):
            return f'{user_id} User\'s password reset!'

        @app.route(self.delete_user_endpoint, methods=['DELETE'])
        def delete_user(realm, user_id):
            self.validate_realm(realm)
            self.cache_handler.delete_cached_user(user_id)

            return '', 200

