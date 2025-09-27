import configparser
import json
import logging

from datetime import datetime
from pathlib import Path
from flask import jsonify
from exception.exceptions import InvalidRealm


def get_epoch_mil_timestamp():
    return int(datetime.now().timestamp() * 1000)  # * 1000 - microseconds to milliseconds

class ConfigHandler:
    def get_config(self, section, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        return dict(config.items(section))

    def get_template(self, template):
        return json.loads(open(template).read())


class Logger:
    def __init__(self, filename):
        # logs/datetime/filename.log
        log_dir = f'logs/{datetime.today().strftime('%Y%m%d_%H%M%S')}'
        self.log = f'{log_dir}/{filename}.log'
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    def get_formatter(self):
        message_format = '%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
        date_format = '%Y/%m/%d %H:%M:%S'

        return logging.Formatter(fmt=message_format, datefmt=date_format)

    def get_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.get_formatter())

        return stream_handler

    def get_file_handler(self):
        file_handler = logging.FileHandler(self.log)
        file_handler.setFormatter(self.get_formatter())

        return file_handler

    def get_logger(self, logger_name=None):
        logger = logging.getLogger(logger_name) if logger_name is not None else logging.getLogger(self.log)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.get_stream_handler())
        logger.addHandler(self.get_file_handler())

        return logger


class KeycloakAPI:
    def __init__(self, logger, config):
        for k, v in config.items():
            setattr(self, k, v)
            logger.info(f'Successfully set \"{self.__class__.__name__}\" class attribute: \"{k}\" = \"{v}\"')

    def validate_realm(self, request_realm):
        if request_realm != self.realm:
            raise InvalidRealm(f'Invalid realm. \"{request_realm}\" does not reflect the configured realm')
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
