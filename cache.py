

class CacheHandler:
    def __init__(self, cache, relay_field, cache_name):
        self.cache = cache
        self.relay_field = relay_field
        self.cache_name = cache_name

    def cache_models(self, value):
        self.cache.delete(self.cache_name)
        self.cache.add(self.cache_name, value)

    def cache_model(self, value):
        cached_models = self.get_cached_models(self.cache_name)
        for model in cached_models:
            if getattr(model, self.relay_field) == getattr(value, self.relay_field):
                cached_models.remove(model)

        cached_models.append(value)

        self.cache.delete(self.cache_name)
        self.cache.add(self.cache_name, cached_models)

    def get_cached_models(self, cache_name):
        cached_models = self.cache.get(cache_name)
        if cached_models is None:
            cached_models = []
            self.cache.add(cache_name, [])

        return cached_models

    def get_cached_model(self, keyword):
        for model in self.get_cached_models(self.cache_name):
            if str(getattr(model, self.relay_field)) == str(keyword):
                return model

        raise KeyError(f'Model with {keyword} value of {self.relay_field} field was not found')

    def delete_cached_model(self, keyword):
        cached_models = self.get_cached_models(self.cache_name)

        for cached_model in cached_models:
            if str(getattr(cached_model, self.relay_field)) == keyword:
                cached_models.remove(cached_model)

        self.cache_models(cached_models)

# Wrappers
class AuthCacheHandler(CacheHandler):
    """
    Wrapper around CacheHandler class.
    Sets an expected field to relay on for queries as "token"
    and cache name as "access_tokens".

    Attributes
    ----------
    cache : flask_caching cache object
    """
    def __init__(self, cache):
        super().__init__(cache, 'token', 'access_tokens')

    def cache_token(self, token):
        self.cache_model(token)

    def get_cached_tokens(self):
        return self.get_cached_models(self.cache_name)

    def get_cached_token(self, access_token):
        return self.get_cached_model(access_token)


class ClientCacheHandler(CacheHandler):
    """
    Wrapper around CacheHandler class.
    Sets an expected field to relay on for queries as "id"
    and cache name as "clients".

    Attributes
    ----------
    cache : flask_caching cache object
    """
    def __init__(self, cache):
        super().__init__(cache, 'id', 'clients')

    def cache_clients(self, clients):
        super().cache_models(clients)

    def cache_client(self, client):
        super().cache_model(client)

    def get_cached_clients(self):
        return super().get_cached_models(self.cache_name)

    def get_cached_client(self, client_id):
        return super().get_cached_model(client_id)

    def delete_cached_client(self, client_id):
        super().delete_cached_model(client_id)

class UserCacheHandler(CacheHandler):
    """
    Wrapper around CacheHandler class.
    Sets an expected field to relay on for queries as "id"
    and cache name as "users".

    Attributes
    ----------
    cache : flask_caching cache object
    """
    def __init__(self, cache):
        super().__init__(cache, 'id', 'users')

    def cache_users(self, users):
        super().cache_models(users)

    def cache_user(self, user):
        super().cache_model(user)

    def get_cached_users(self):
        return super().get_cached_models(self.cache_name)

    def get_cached_user(self, user_id):
        return super().get_cached_model(user_id)

    def delete_cached_user(self, user_id):
        super().delete_cached_model(user_id)


class UsergroupCacheHandler(CacheHandler):
    """
    Wrapper around CacheHandler class.
    Sets an expected field to relay on for queries as "id"
    and cache name as "usergroups".

    Attributes
    ----------
    cache : flask_caching cache object
    """
    def __init__(self, cache):
        super().__init__(cache, 'id', 'usergroups')

    def cache_usergroups(self, usergroups):
        super().cache_models(usergroups)

    def cache_usergroup(self, usergroup):
        super().cache_model(usergroup)

    def get_cached_usergroups(self):
        return super().get_cached_models(self.cache_name)

    def get_cached_usergroup(self, usergroup_id):
        return super().get_cached_model(usergroup_id)

    def delete_cached_usergroup(self, usergroup_id):
        super().delete_cached_model(usergroup_id)

