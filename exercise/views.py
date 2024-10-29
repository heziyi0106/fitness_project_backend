from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import timedelta
from .models import Exercise
from .serializers import ExerciseSerializer

class MonthlyPlansView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        返回當前用戶最近一個月的運動計劃
        """
        user = request.user
        one_month_ago = now() - timedelta(days=30)
        # 使用 prefetch_related 來一次性獲取相關的 ExerciseSet 和 SetDetail
        monthly_plans = Exercise.objects.filter(user=request.user, created_at__gte=one_month_ago).prefetch_related('sets__details')
        serializer = ExerciseSerializer(monthly_plans, many=True)
        return Response(serializer.data)


class WeeklyPlansView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        返回當前用戶最近一周的運動計劃
        """
        user = request.user
        one_week_ago = now() - timedelta(days=7)
        # 使用 prefetch_related 來一次性獲取相關的 ExerciseSet 和 SetDetail
        weekly_plans = Exercise.objects.filter(user=request.user, created_at__gte=one_week_ago).prefetch_related('sets__details')
        serializer = ExerciseSerializer(weekly_plans, many=True)
        return Response(serializer.data)
