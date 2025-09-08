import copy
import json
from uuid import uuid4

from flask import request, jsonify

from exception.exceptions import InvalidRealm
from utils import Logger, UsergroupCacheHandler

logger = Logger('usergroup')
logger = logger.get_logger()

class Usergroup:
    def __init__(self, **kwargs):
        self.id = str(uuid4())
        # Minimal required args to build a Keycloak user group
        required_args = ['name']
        logger.info(f'Initializing a usergroup\n'
                    f'Required arguments: {required_args}\n'
                    f'UID: {self.id}')

        if 'usergroup_dict' in kwargs:
            usergroup_dict = kwargs['usergroup_dict']
            if set(required_args).issubset(set(usergroup_dict)):
                for k, v in usergroup_dict.items():
                    setattr(self, k, v)
                    logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')
        elif set(required_args).issubset(set(kwargs)):
            for k, v in kwargs.items():
                setattr(self, k, v)
                logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')
        else:
            message = ('Usergroup object is missing required arguments.'
                       ' Valid arguments were not given nor was a valid dict representation.')
            logger.error(message)
            raise ValueError(message)

        self.path = f'/{self.name}'

    def make_template(self, template):
        for key in template.keys():
            if key in self.__dict__.keys():
                template[key] = getattr(self, key)

        return template


class UsergroupAPI:
    def __init__(self, cache, config):
        self.cache_handler = UsergroupCacheHandler(cache)
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
            try:
                usergroup = Usergroup(usergroup_dict=dict(request.json))
                self.cache_handler.cache_usergroup(usergroup)
            except ValueError as exception:
                return jsonify({
                    'error': 'invalid_request',
                    'error_description': str(exception)
                }), 400
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

        @app.route(self.delete_usergroup_endpoint, methods=['DELETE'])
        def delete_usergroup(realm, usergroup_id):
            self.validate_realm(realm)

            self.cache_handler.delete_cached_usergroup(usergroup_id)

            return '', 200

