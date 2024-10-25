from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ExerciseType, Exercise, ExerciseSet, SetDetail, Template, duplicate_template
from .serializers import ExerciseTypeSerializer, ExerciseSerializer, ExerciseSetSerializer, SetDetailSerializer, TemplateSerializer

# 運動類型視圖
class ExerciseTypeListCreateView(generics.ListCreateAPIView):
    queryset = ExerciseType.objects.all()
    serializer_class = ExerciseTypeSerializer

# 獲取和創建運動計劃的視圖
class ExerciseListCreateView(generics.ListCreateAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

# 獲取、更新、刪除單個運動計劃的視圖
class ExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer

# 獲取和創建 ExerciseSet 的視圖
class ExerciseSetListCreateView(generics.ListCreateAPIView):
    queryset = ExerciseSet.objects.all()
    serializer_class = ExerciseSetSerializer

# 獲取、更新、刪除單個 ExerciseSet 的視圖
class ExerciseSetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExerciseSet.objects.all()
    serializer_class = ExerciseSetSerializer

# 獲取和創建 SetDetail 的視圖
class SetDetailListCreateView(generics.ListCreateAPIView):
    queryset = SetDetail.objects.all()
    serializer_class = SetDetailSerializer

# 獲取、更新、刪除單個 SetDetail 的視圖
class SetDetailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SetDetail.objects.all()
    serializer_class = SetDetailSerializer

# 範本管理視圖
class TemplateListCreateView(generics.ListCreateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

# 獲取、更新、刪除單個範本的視圖
class TemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

# 根據範本創建新的運動
class CreateExerciseFromTemplateView(APIView):
    """
    基於範本創建新的運動
    """
    def post(self, request, template_id):
        try:
            template = Template.objects.get(id=template_id)
            new_exercises = []
            
            for exercise in template.exercises.all():
                new_exercise = Exercise.objects.create(
                    name=exercise.name,
                    total_duration=exercise.total_duration,
                    goal=exercise.goal,
                    exercise_type=exercise.exercise_type
                )
                
                # 複製每個 ExerciseSet 和 SetDetail
                for exercise_set in exercise.sets.all():
                    new_exercise_set = ExerciseSet.objects.create(
                        exercise=new_exercise,
                        exercise_name=exercise_set.exercise_name,
                        body_part=exercise_set.body_part,
                        joint_type=exercise_set.joint_type,
                        sets=exercise_set.sets
                    )
                    
                    for detail in exercise_set.details.all():
                        SetDetail.objects.create(
                            exercise_set=new_exercise_set,
                            reps=detail.reps,
                            weight=detail.weight,
                            actual_duration=detail.actual_duration,
                            rest_time=detail.rest_time
                        )
                        
                new_exercises.append(new_exercise)
            
            return Response({"message": "Exercise(s) created from template", "exercises": [ExerciseSerializer(ex).data for ex in new_exercises]}, status=status.HTTP_201_CREATED)
        
        except Template.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)

# 複製範本並重新命名
class DuplicateTemplateView(APIView):
    """
    複製範本並命名
    """
    def post(self, request, template_id):
        new_name = request.data.get('name')
        if not new_name:
            return Response({"error": "New template name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_template = duplicate_template(template_id, new_name)
            return Response({"message": "Template duplicated", "template": TemplateSerializer(new_template).data}, status=status.HTTP_201_CREATED)
        
        except Template.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
