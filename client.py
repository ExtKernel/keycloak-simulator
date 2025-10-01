from uuid import uuid4
from flask import app, request
from utils import Logger, KeycloakAPI
from cache import ClientCacheHandler

logger = Logger('client')
logger = logger.get_logger()


class Client:
    def __init__(self, **kwargs):
        self.id = str(uuid4())
        host = f'{request.scheme}://{request.host}'
        self.rootUrl = host
        self.baseUrl = host
        self.adminUrl = host
        self.redirectUris = '*'
        self.webOrigins = '*'
        self.enabled = True
        self.authorizationServicesEnabled = True
        self.standardFlowEnabled = True
        self.implicitFlowEnabled = True
        self.directAccessGrantsEnabled = True

        required_args = ['clientId']
        logger.info(f'Initializing a client with UID: {self.id}')
        logger.info(f'Required arguments to build \"{self.__class__.__name__}\": {required_args}')

        arguments_dict = None
        if 'client_dict' in kwargs:
            client_dict = kwargs['client_dict']
            if set(required_args).issubset(set(client_dict.keys())):
                arguments_dict = client_dict
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

        self.name = self.clientId


class ClientAPI(KeycloakAPI):
    def __init__(self, cache, config):
        super().__init__(logger, config)
        self.cache_handler = ClientCacheHandler(cache)

        required_args = ['clientId']
        logger.info(f'Initializing a user\n'
                    f'Required arguments: {required_args}\n'
                    f'UID: {self.id}\nUNIX timestamp: {self.createdTimestamp}')

    def init_endpoints(self):
        """
        Master function for initializing client-related endpoints.

        :param app: flask app.
        :return: depends on the endpoint.
        """
        self.init_error_handlers(app)

        @app(self.create_client_endpoint, method=['POST'])
        def create_client(realm):
            self.validate_realm(realm)

            client = Client(client_dict=dict(request.json))
            self.cache_handler.cache_client(client)

            return '', 201

