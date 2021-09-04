from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import APIException

__author__ = 'Mahmud'

from django_classic.extras.classic_cache import ClassicCache


class ClassicTokenAuthentication(TokenAuthentication):
    cache_key = 'ClassicTokenAuthentication'

    def perform_token_authentication(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User ' + str(token.user.username) + ' inactive or deleted.')
        return token.user, token

    def attempt_cached_authentication(self, key):
        cache_key = self.cache_key + str(key)
        cached_token = ClassicCache.get_by_key(key=cache_key)
        if cached_token is None:
            cached_token = self.perform_token_authentication(key=key)
            ClassicCache.set_by_key(key=cache_key, value=cached_token, expiry=24 * 60 * 60)
        return cached_token

    def authenticate_credentials(self, key):
        return self.attempt_cached_authentication(key=key)

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or len(auth) == 0 or auth[0].lower() != b'token':
            return None
        if len(auth) <= 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        try:
            auth_user, token = self.authenticate_credentials(auth[1])
        except exceptions.AuthenticationFailed as error:
            raise error
        except APIException as error:
            raise error
        except Exception as error:
            raise APIException(str(error))
        return auth_user, token
