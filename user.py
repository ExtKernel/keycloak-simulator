import copy
import json
from uuid import uuid4

from flask import request, jsonify
from exception.exceptions import NoAdminUser
from utils import (
    Logger,
    ConfigHandler,
    get_epoch_mil_timestamp,
    KeycloakAPI
)
from cache import UserCacheHandler, UsergroupCacheHandler

logger = Logger('user')
logger = logger.get_logger()


class User:
    def __init__ (self, **kwargs):
        self.id = str(uuid4())
        self.createdTimestamp = get_epoch_mil_timestamp()

        required_args = ['username', 'firstName', 'lastName', 'email', 'enabled']
        logger.info(f'Initializing a user\n'
                    f'Required arguments: {required_args}\n'
                    f'UID: {self.id}\nUNIX timestamp: {self.createdTimestamp}')

        arguments_dict = None
        if 'user_dict' in kwargs:
            user_dict = kwargs['user_dict']
            if set(required_args).issubset(set(user_dict.keys())):
                arguments_dict = user_dict
        elif set(required_args).issubset(set(kwargs)):
            arguments_dict = kwargs.items()
        else:
            message = (f'\"{self.__class__.__name__}\" object is missing required arguments.'
                       ' Valid arguments were not given nor was a valid dict representation.')
            logger.error(message)
            raise ValueError(message)

        for k, v in arguments_dict.items():
            setattr(self, k, v)
            logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\" dynamically')

    def check_credentials(self):
        credentials_fields = ['value', 'temporary']
        return True if set(self.credentials.keys()) == set(credentials_fields) else False

    def make_template(self, template):
        for key in template.keys():
            if key in self.__dict__.keys():
                template[key] = getattr(self, key)

        return template


class UserAPI(KeycloakAPI):
    def __init__ (self, cache, config):
        super().__init__(logger, config)
        self.config_handler = ConfigHandler()
        self.cache_handler = UserCacheHandler(cache)
        # Usergroup uses the same cache as User at the moment
        # Change this if usergroups will be ever created with a different cache
        self.usergroup_cache_handler = UsergroupCacheHandler(cache)

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

            user = User(user_dict=dict(request.json))
            self.cache_handler.cache_user(user)

            return '', 201

        @app.route(self.get_user_endpoint, methods=['GET'])
        def get_user(realm, user_id):
            self.validate_realm(realm)

            user = self.cache_handler.get_cached_user(user_id)
            template = json.loads(open(self.get_user_response_template).read())

            return jsonify(user.make_template(template))

        @app.route(self.get_users_endpoint, methods=['GET'])
        def get_users(realm):
            self.validate_realm(realm)

            template = json.loads(open(self.get_users_response_template).read())
            users = []
            for user in self.cache_handler.get_cached_users():
                users.append(user.make_template(copy.deepcopy(template)))

            return jsonify(users)

        @app.route(self.usergroup_add_user_endpoint, methods=['PUT'])
        def add_usergroup(realm, user_id, usergroup_id):
            self.validate_realm(realm)

            usergroup = self.usergroup_cache_handler.get_cached_usergroup(usergroup_id)
            user = self.cache_handler.get_cached_user(user_id)

            usergroup.users.add(user)
            self.usergroup_cache_handler.cache_usergroup(usergroup)

            return '', 204

        @app.route(self.reset_user_password_endpoint, methods=['PUT'])
        def reset_password(realm, user_id):
            self.validate_realm(realm)

            user = self.cache_handler.get_cached_user(user_id)
            request_credentials = json.loads(request.data)['credentials']

            if user.check_credentials():
                user.credentials['value'] = request_credentials['value']
                user.credentials['temporary'] = request_credentials['temporary']

                self.cache_handler.cache_user(user)
            else:
                user.credentials = {
                    'value': request_credentials['value'],
                    'temporary': request_credentials['temporary']
                }

            return '', 204

        @app.route(self.usergroup_remove_user_endpoint, methods=['DELETE'])
        def remove_usergroup(realm, user_id, usergroup_id):
            self.validate_realm(realm)

            usergroup = self.usergroup_cache_handler.get_cached_usergroup(usergroup_id)
            user = self.cache_handler.get_cached_user(user_id)

            usergroup.users.remove(user)
            self.usergroup_cache_handler.cache_usergroup(usergroup)

            return '', 204

        @app.route(self.delete_user_endpoint, methods=['DELETE'])
        def delete_user(realm, user_id):
            self.validate_realm(realm)

            self.cache_handler.delete_cached_user(user_id)

            return '', 200
