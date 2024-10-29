from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.conf import settings

class ExpiringToken(Token):
    class Meta:
        proxy = True  # 使用代理模型，不修改原始表

    def is_expired(self):
        # 设置 token 的过期时间
        expiration_time = self.created + settings.TOKEN_EXPIRATION_TIME
        return timezone.now() > expiration_time

