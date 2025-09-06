import json
import random
import string

from uuid import uuid4
from flask import jsonify
from utils import Logger

logger = Logger('auth')
logger = logger.get_logger()


def generate_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class AuthAPI:
    def __init__(self, config):
        for k, v in config.items():
            setattr(self, k, v)

    def validate_realm(self, request_realm):
        if request_realm != self.realm:
            message = f'Invalid realm. \"{request_realm}\" does not reflect the configured realm'
            logger.error(message)
            raise ValueError(message)
        return True

    def get_template(self, template):
        return json.loads(open(template).read())

    def init_endpoints(self, app):
        @app.route(self.token_endpoint, methods=['POST'])
        def get_token(realm):
            self.validate_realm(realm)

            template = self.get_template(self.token_response_template)
            template['access_token'] = generate_string(771)
            template['refresh_token'] = generate_string(612)
            template['id_token'] = uuid4()
            template['session_state'] = generate_string(36)

            return jsonify(template)

        @app.route(self.introspect_endpoint, methods=['POST'])
        def introspect(realm):
            self.validate_realm(realm)

            return self.get_template(self.introspect_response_template)