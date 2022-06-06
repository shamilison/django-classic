__author__ = 'shamilsakib'

from django.core.cache import cache
import logging

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


class ClassicCache(object):
    @classmethod
    def get_by_key(cls, key):
        try:
            return cache.get(key)
        except Exception as error:
            logger.exception(error)
            return None

    @classmethod
    def set_by_key(cls, key, value, expiry):
        try:
            return cache.set(key, value, expiry)
        except Exception as error:
            logger.exception(error)
            return None

    @classmethod
    def clear_by_key(cls, key):
        try:
            cache.delete(key)
        except Exception as error:
            logger.exception(error)

    @classmethod
    def clear_keys_with_pattern(cls, pattern, version=None):
        try:
            cache.delete_pattern(pattern, version=version)
        except Exception as error:
            logger.exception(error)
