from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import APIException

__author__ = 'Mahmud'

from django_classic.extras.classic_cache import ClassicCache


class ClassicTokenAuthentication(TokenAuthentication):
    cache_key = 'ClassicTokenAuthentication'

    def perform_token_authentication(self, auth_key):
        model = self.get_model()
        try:
            token = model.objects.get(key=auth_key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User ' + str(token.user.username) + ' inactive or deleted.')
        return token.user, token

    def attempt_cached_authentication(self, auth_key):
        cache_key = self.cache_key + str(auth_key)
        cached_value = ClassicCache.get_by_key(key=cache_key)
        if cached_value is None:
            cached_value = self.perform_token_authentication(auth_key=auth_key)
            ClassicCache.set_by_key(key=cache_key, value=cached_value, expiry=24 * 60 * 60)
        return cached_value

    def authenticate_credentials(self, auth_key):
        return self.attempt_cached_authentication(auth_key=auth_key)

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
            _auth_key = auth[1].decode() if isinstance(auth[1], bytes) else auth[1]
            _auth_user, _token = self.authenticate_credentials(auth_key=_auth_key)
        except exceptions.AuthenticationFailed as error:
            raise error
        except APIException as error:
            raise error
        except Exception as error:
            raise APIException(str(error))
        return _auth_user, _token
