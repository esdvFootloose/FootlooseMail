from .transip import TransipApi
from FootlooseMail.secret import transip_username, transip_password
from django.core.cache import cache

def get_api():
    api = cache.get('api')
    if api is not None:
        return api
    api = TransipApi()
    api.login(transip_username, transip_password)
    if not api.logged_in:
        return None
    cache.set('api', api, 24*60*60)
    return api

def fetch_alias(use_cache):
    api = get_api()
    if use_cache:
        if api.groups != {}:
            return api.groups
    if api is None:
        return None
    aliasses = api.fetch_data()
    cache.set('api', api, 24*60*60)
    return aliasses