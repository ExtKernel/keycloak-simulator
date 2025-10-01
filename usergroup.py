import copy
import json
from uuid import uuid4

from flask import request, jsonify
from utils import Logger, KeycloakAPI
from cache import UsergroupCacheHandler

logger = Logger('usergroup')
logger = logger.get_logger()

class Usergroup:
    def __init__(self, **kwargs):
        self.id = str(uuid4())

        required_args = ['name']
        logger.info(f'Initializing a usergroup with UID: {self.id}')
        logger.info(f'Required arguments to build \"{self.__class__.__name__}\": {required_args}')

        arguments_dict = None
        if 'usergroup_dict' in kwargs:
            usergroup_dict = kwargs['usergroup_dict']
            if set(required_args).issubset(set(usergroup_dict)):
                arguments_dict = usergroup_dict
        elif set(required_args).issubset(set(kwargs)):
            arguments_dict = kwargs
        else:
            message = (f'\"{self.__class__.__name__}\" object is missing required arguments.'
                       ' Valid arguments were not given nor was a valid dict representation.')
            logger.error(message)
            raise ValueError(message)

        for k, v in arguments_dict.items():
            setattr(self, k, v)
            logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\" dynamically')

        # Set users to an empty list to avoid exceptions
        # And redundant None-checking
        if 'users' not in list(arguments_dict.keys()):
            self.users = []

        self.path = f'/{self.name}'

    def make_template(self, template):
        for key in template.keys():
            if key in self.__dict__.keys():
                template[key] = getattr(self, key)

        return template


class UsergroupAPI(KeycloakAPI):
    def __init__(self, cache, config):
        super().__init__(logger, config)
        self.cache_handler = UsergroupCacheHandler(cache)

    def init_endpoints(self, app):
        """
        Master function for initializing usergroup-related endpoints.

        :param app: flask app.
        :return: depends on the endpoint.
        """
        self.init_error_handlers(app)

        @app.route(self.create_usergroup_endpoint, methods=['POST'])
        def create_usergroup(realm):
            self.validate_realm(realm)

            usergroup = Usergroup(usergroup_dict=dict(request.json))
            self.cache_handler.cache_usergroup(usergroup)

            return '', 201

        @app.route(self.get_usergroup_endpoint, methods=['GET'])
        def get_usergroup(realm, usergroup_id):
            self.validate_realm(realm)

            usergroup = self.cache_handler.get_cached_usergroup(usergroup_id)
            template = json.loads(open(self.get_usergroup_response_template).read())

            return jsonify(usergroup.make_template(template))

        @app.route(self.get_usergroups_endpoint, methods=['GET'])
        def get_usergroups(realm):
            self.validate_realm(realm)

            template = json.loads(open(self.get_usergroups_response_template).read())
            usergroups = []
            for usergroup in self.cache_handler.get_cached_usergroups():
                usergroups.append(usergroup.make_template(copy.deepcopy(template)))

            return jsonify(usergroups)

        @app.route(self.get_usergroup_members_endpoint, methods=['GET'])
        def get_usergroup_members(realm, usergroup_id):
            self.validate_realm(realm)

            usergroup = self.cache_handler.get_cached_usergroup(usergroup_id)

            return usergroup.users

        @app.route(self.delete_usergroup_endpoint, methods=['DELETE'])
        def delete_usergroup(realm, usergroup_id):
            self.validate_realm(realm)

            self.cache_handler.delete_cached_usergroup(usergroup_id)

            return '', 200

