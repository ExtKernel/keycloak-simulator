import json
import logging
import configparser
from pathlib import Path
from datetime import datetime


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


class CacheHandler:
    def __init__(self, cache):
        self.cache = cache

    def get_cached_models(self, cache_name):
        cached_models = self.cache.get(cache_name)
        if cached_models is None:
            cached_models = []
            self.cache.add(cache_name, [])

        return cached_models

    def get_cached_model(self, relay_field, keyword, cache_name):
        for model in self.get_cached_models(cache_name):
            if str(getattr(model, relay_field)) == str(keyword):
                return model

        raise KeyError(f'Model with {keyword} value of {relay_field} field was not found')

    def cache_model(self, cache_name, value):
        cached_model = self.get_cached_models(cache_name)
        cached_model.append(value)

        self.cache.delete(cache_name)
        self.cache.add(cache_name, cached_model)


class AuthCacheHandler(CacheHandler):
    def __init__(self, cache):
        super().__init__(cache)
        self.access_token_cache_name = 'access_tokens'

    def get_cached_tokens(self):
        return self.get_cached_models(self.access_token_cache_name)

    def get_cached_token(self, access_token):
        return self.get_cached_model('token', access_token, self.access_token_cache_name)

    def cache_token(self, token):
        self.cache_model(self.access_token_cache_name, token)


class UserCacheHandler(CacheHandler):
    def __init__(self, cache):
        super().__init__(cache)
        self.user_cache_name = 'users'

    def get_cached_users(self):
        return self.get_cached_models(self.user_cache_name)

    def get_cached_user(self, user_id):
        return self.get_cached_model('id', user_id, self.user_cache_name)

    def cache_user(self, user):
        self.cache_model(self.user_cache_name, user)

    def cache_users(self, users):
        self.cache.delete(self.user_cache_name)
        self.cache.add(self.user_cache_name, users)

    def delete_cached_user(self, user_id):
        cached_users = self.get_cached_users()

        for user in cached_users:
            print(user)
            if str(user.id) == user_id:
                cached_users.remove(user)

        self.cache_users(cached_users)

