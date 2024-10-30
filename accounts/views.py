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
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': '成功訪問受保護的資源'})


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
        # 驗證使用者
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # 查找現有 token 或創建一個新的 token
        token, created = ExpiringToken.objects.get_or_create(user=user)

        # 如果 token 存在且沒有過期，就更新過期時間
        if not created:
            if token.is_expired():
                # 如果過期，刪除舊 token 並創建新 token
                token.delete()
                token = ExpiringToken.objects.create(user=user)
            else:
                # 重置 token 的過期時間
                token.created = timezone.now()
                token.save()

        # 返回 token 和過期時間
        expires_in = settings.TOKEN_EXPIRATION_TIME.total_seconds()
        return Response({'token': token.key, 'expires_in': expires_in})


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


