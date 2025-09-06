import json
import random
import string

from uuid import uuid4
from flask import jsonify, request
from utils import (
    Logger,
    ConfigHandler,
    AuthCacheHandler,
    UserCacheHandler,
    get_epoch_mil_timestamp
)

logger = Logger('auth')
logger = logger.get_logger()

def generate_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class AccessToken:
    def __init__(
            self,
            token,
            expires_in,
            id_token,
            session_state
    ):
        self.token = token
        self.expires_in = expires_in
        self.id_token = id_token
        self.session_state = session_state
        self.issued_at = get_epoch_mil_timestamp()

class AuthAPI:
    def __init__(
            self,
            cache,
            config,
            admin_user
    ):
        self.admin_user = admin_user
        self.config_handler = ConfigHandler()
        self.cache_handler = AuthCacheHandler(cache)
        # Set config entries as attributes
        for k, v in config.items():
            setattr(self, k, v)
            logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')

    def validate_realm(self, request_realm):
        if request_realm != self.realm:
            message = f'Invalid realm. \"{request_realm}\" does not reflect the configured realm'
            logger.error(message)
            raise ValueError(message)
        return True

    def set_instrospect_template_realm_roles(
            self,
            introspect_template,
            realm_roles_template
    ):
        for key in realm_roles_template.keys():
            introspect_template[key] = realm_roles_template[key]

        return introspect_template

    def init_endpoints(self, app):
        @app.route(self.token_endpoint, methods=['POST'])
        def get_token(realm):
            self.validate_realm(realm)
            template = self.config_handler.get_template(self.token_response_template)

            access_token = AccessToken(
                token=generate_string(771),
                expires_in=template['expires_in'],
                id_token=uuid4(),
                session_state=generate_string(36)
            )
            self.cache_handler.cache_token(access_token)

            template['access_token'] = access_token.token
            template['refresh_token'] = generate_string(612)
            template['id_token'] = access_token.id_token
            template['session_state'] = access_token.session_state

            return jsonify(template)

        @app.route(self.introspect_endpoint, methods=['POST'])
        def introspect(realm):
            self.validate_realm(realm)

            # Add Realm roles from the template to the introspect response template
            introspect_response = self.set_instrospect_template_realm_roles(
                self.config_handler.get_template(self.introspect_response_template
                ),
                self.config_handler.get_template(self.realm_roles_template)
            )
            introspect_response['sub'] = self.admin_user.id
            # Fields that require data from the token
            token = request.form['token']
            access_token = self.cache_handler.get_cached_token(token)
            introspect_response['sid'] = access_token.session_state
            introspect_response['exp'] = access_token.issued_at + int(access_token.expires_in)
            introspect_response['iat'] = access_token.issued_at
            # Fields having Client ID as a value
            client_id = request.form['client_id']
            introspect_response['azp'] = client_id
            introspect_response['client_id'] = client_id
            # Fields having username as a value
            username = request.form['username']
            introspect_response['username'] = username
            introspect_response['preferred_username'] = username
            # HTTP Protocol + :// + this server host (from the request) + endpoint
            introspect_response['iss'] = f'{request.scheme}://{request.host}/realms/{self.master_realm}'
            # "onltro:" + generated UID (at the moment of writing this comment)
            introspect_response['jti'] = introspect_response['jti'] + str(uuid4())

            return introspect_response

