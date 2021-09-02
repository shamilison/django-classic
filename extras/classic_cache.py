from django.core.cache import cache

__author__ = 'shamilsakib'


class ClassicCache(object):
    @classmethod
    def get_by_key(cls, key):
        return cache.get(key)

    @classmethod
    def set_by_key(cls, key, value, expiry):
        return cache.set(key, value, expiry)

    @classmethod
    def clear_by_key(cls, key):
        cache.delete(key)

    @classmethod
    def clear_keys_with_pattern(cls, pattern, version=None):
        cache.delete_pattern(pattern, version=version)
