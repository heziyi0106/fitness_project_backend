from django.forms import ValidationError
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import timedelta
from .models import Exercise, BodyComposition, ExerciseSet, SetDetail, Template, save_as_template, create_from_template
from .serializers import ExerciseSerializer, BodyCompositionSerializer, TemplateSerializer

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

class BodyCompositionDetailView(APIView):
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
        
    def post(self, request):
        """
        創建或更新當前用戶的身體組成數據
        """
        user = request.user
        serializer = BodyCompositionSerializer(data=request.data)
        
        if serializer.is_valid():
            # 使用 validated_data 創建新的 BodyComposition 實例
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TemplateListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        創建計劃模板
        """
        user = request.user
        template_name = request.data.get('name')
        goal = request.data.get('goal')
        exercise_type_data = request.data.get('exercise_type', [])
        total_duration = request.data.get('total_duration')
        sets_data = request.data.get('sets', [])

        if not template_name:
            return Response({'error': '模板名稱是必需的'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            template = Template.objects.create(name=template_name)
            exercises = []

            for set_data in sets_data:
                exercise = Exercise.objects.create(
                    name=template_name,
                    goal=goal,
                    total_duration=total_duration,
                    user=user
                )
                # 設定運動類型和其他詳細信息
                exercise.exercise_type.set(exercise_type_data)

                exercise_sets = []
                for detail_data in set_data['details']:
                    exercise_set = ExerciseSet.objects.create(
                        exercise=exercise,
                        exercise_name=set_data['exercise_name'],
                        body_part=set_data['body_part'],
                        joint_type=set_data['joint_type'],
                        sets=len(set_data['details'])
                    )
                    # 創建 SetDetail
                    SetDetail.objects.bulk_create([
                        SetDetail(
                            exercise_set=exercise_set,
                            reps=detail['reps'],
                            weight=detail['weight'],
                            actual_duration=detail['actual_duration'],
                            rest_time=detail['rest_time']
                        )
                        for detail in detail_data
                    ])
                    exercise_sets.append(exercise_set)
                exercises.append(exercise)

            # 將這些創建的運動計劃添加到模板中
            template.exercises.set(exercises)

            serializer = TemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TemplateDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, template_id):
        """
        獲取特定模板的詳細信息
        """
        try:
            template = Template.objects.get(id=template_id, exercises__user=request.user)
            serializer = TemplateSerializer(template)
            return Response(serializer.data)
        except Template.DoesNotExist:
            return Response({'error': '模板不存在'}, status=status.HTTP_404_NOT_FOUND)

class CreateFromTemplateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, template_id):
        """
        使用模板創建新的運動計劃
        """
        try:
            new_exercises = create_from_template(template_id, request.user)
            return Response({'message': '成功創建運動計劃'}, status=status.HTTP_201_CREATED)
        except Template.DoesNotExist:
            return Response({'error': '模板不存在'}, status=status.HTTP_404_NOT_FOUND)
