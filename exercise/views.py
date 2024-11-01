from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import timedelta
from .models import Exercise, BodyComposition
from .serializers import ExerciseSerializer, BodyCompositionSerializer

class MonthlyPlansView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        返回當前用戶最近一個月的運動計劃
        """
        user = request.user
        one_month_ago = now() - timedelta(days=30)
        
        # 使用 prefetch_related 來優化數據庫查詢，獲取 ExerciseSet 和 SetDetail
        monthly_plans = Exercise.objects.filter(
            user=user,
            created_at__gte=one_month_ago
        ).prefetch_related('sets__details')
        
        # 序列化數據
        serializer = ExerciseSerializer(monthly_plans, many=True)
        
        # 檢查結果並返回數據
        if monthly_plans.exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([])

class WeeklyPlansView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        返回當前用戶最近一周的運動計劃
        """
        user = request.user
        one_week_ago = now() - timedelta(days=7)
        
        # 使用 prefetch_related 來優化數據庫查詢，獲取 ExerciseSet 和 SetDetail
        weekly_plans = Exercise.objects.filter(
            user=user,
            created_at__gte=one_week_ago
        ).prefetch_related('sets__details')
        
        # 序列化數據
        serializer = ExerciseSerializer(weekly_plans, many=True)
        
        # 檢查結果並返回數據
        if weekly_plans.exists():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([])


class BodyCompositionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        返回當前用戶的最新身體狀態數據
        """
        user = request.user
        # 獲取當前用戶的最新身體狀態數據
        body_composition = BodyComposition.objects.filter(user=user).order_by('-measured_at').first()

        if body_composition:
            serializer = BodyCompositionSerializer(body_composition)
            return Response(serializer.data)
        else:
            return Response({})
        

class CreateExercisePlanView(generics.CreateAPIView):
    serializer_class = ExerciseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # 在保存計劃時自動將當前用戶設為計劃的擁有者
        serializer.save(user=self.request.user)

        # 返回成功創建的響應
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)