from rest_framework import serializers
from .models import Exercise, ExerciseSet, Template

class ExerciseSetSerializer(serializers.ModelSerializer):
    total_reps = serializers.IntegerField(source='total_reps', read_only=True)  # 使用模型方法

    class Meta:
        model = ExerciseSet
        fields = ['exercise_name', 'body_part', 'sets', 'reps_per_set', 'weight', 'total_reps']


class ExerciseSerializer(serializers.ModelSerializer):
    sets = ExerciseSetSerializer(many=True)  # 嵌套 ExerciseSet

    class Meta:
        model = Exercise
        fields = ['name', 'total_duration', 'goal', 'date', 'sets']


class TemplateSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer()  # 範本中嵌套運動

    class Meta:
        model = Template
        fields = ['id', 'name', 'exercise', 'created_at']
