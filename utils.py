import logging
import configparser
from pathlib import Path
from datetime import datetime


class Logger:
    def __init__(self, filename):
        # logs/datetime/filename.log
        log_dir = f'logs/{datetime.today().strftime('%Y%m%d_%H%M%S')}'
        self.log = f'{log_dir}/{filename}.log'
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    def get_formatter(self):
        message_format = '[%(asctime)s] [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
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


def get_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    return dict(config.items('Keycloak'))

