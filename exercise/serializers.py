from rest_framework import serializers
from .models import Exercise, ExerciseSet, SetDetail, BodyComposition

class ExerciseSerializer(serializers.ModelSerializer):
    sets = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = ['id', 'name', 'goal', 'total_duration', 'calculated_calories_burned', 'manual_calories_burned', 'scheduled_date', 'created_at', 'sets']

    def get_sets(self, obj):
        # 自定義方法來獲取 ExerciseSet 的數據
        sets = ExerciseSet.objects.filter(exercise=obj)
        result = []
        for set_obj in sets:
            set_details = SetDetail.objects.filter(exercise_set=set_obj)
            result.append({
                "exercise_name": set_obj.exercise_name,
                "body_part": set_obj.body_part,
                "joint_type": set_obj.joint_type,
                "sets": set_obj.sets,
                "details": [
                    {
                        "reps": detail.reps,
                        "weight": detail.weight,
                        "actual_duration": detail.actual_duration,
                        "rest_time": detail.rest_time
                    }
                    for detail in set_details
                ]
            })
        return result
    
class BodyCompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyComposition
        fields = '__all__'