from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ExpiringToken

class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        token = ExpiringToken.objects.get(key=key)
        if token.is_expired():
            token.delete()  # 删除过期 token
            raise AuthenticationFailed('Token has expired')
        return (token.user, token)
