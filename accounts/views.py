from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from .authentication import ExpiringToken

# 使用者註冊 API
@api_view(['POST'])
@permission_classes([AllowAny])  # 註冊API不需要身份驗證
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if username and password:
        user = User.objects.create_user(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)
    return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


# 登入獲取 Token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # 验证用户
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # 查找现有 token
        token, created = ExpiringToken.objects.get_or_create(user=user)

        # 检查 token 是否过期
        if not created:
            if token.is_expired():
                # 如果过期，删除旧 token 并生成新 token
                token.delete()
                token = ExpiringToken.objects.create(user=user)

        return Response({'token': token.key})


# 登出 API
@api_view(['POST'])
def logout(request):
    # 獲取請求中的 Token
    token_key = request.auth
    if token_key:
        try:
            # 找到對應的 Token 並删除
            token = Token.objects.get(key=token_key)
            token.delete()
            return Response({"message": "登出成功"}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"error": "Token 不存在"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "未提供 Token"}, status=status.HTTP_400_BAD_REQUEST)
