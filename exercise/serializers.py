from rest_framework import serializers
from .models import ExerciseType, Exercise, ExerciseSet, SetDetail, Template

class ExerciseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseType
        fields = ['id', 'name', 'description']  # 將模型的字段序列化

class SetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetDetail
        fields = ['id', 'reps', 'weight', 'actual_duration', 'rest_time']  # 包含所有 SetDetail 的細節

class ExerciseSetSerializer(serializers.ModelSerializer):
    details = SetDetailSerializer(many=True, read_only=True)  # 多個 SetDetail

    class Meta:
        model = ExerciseSet
        fields = ['id', 'exercise_name', 'body_part', 'joint_type', 'sets', 'details']  # 包含 SetDetail 和其他欄位

class ExerciseSerializer(serializers.ModelSerializer):
    sets = ExerciseSetSerializer(many=True, read_only=True)  # 多個 ExerciseSet

    class Meta:
        model = Exercise
        fields = ['id', 'name', 'goal', 'total_duration', 'exercise_type', 'sets']  # 包含 ExerciseSet 和相關的欄位

class TemplateSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)  # 多個 Exercise

    class Meta:
        model = Template
        fields = ['id', 'name', 'exercises', 'created_at', 'updated_at']  # 包含範本的名稱和所有運動
