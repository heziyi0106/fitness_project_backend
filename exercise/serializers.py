from rest_framework import serializers
from .models import BodyComposition, Exercise, ExerciseSet, SetDetail, ExerciseType, Template

class BodyCompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyComposition
        fields = [
            'height', 'weight', 'body_fat_percentage', 'muscle_mass', 'bmi',
            'visceral_fat', 'basal_metabolic_rate', 'waist_circumference', 
            'hip_circumference', 'chest_circumference', 'shoulder_circumference', 
            'upper_arm_circumference', 'lower_arm_circumference', 'thigh_circumference',
            'calf_circumference', 'measured_at'
        ]
        read_only_fields = ['bmi']

class ExerciseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseType
        fields = ['id', 'name', 'description']

class SetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetDetail
        fields = ['reps', 'weight', 'actual_duration', 'rest_time']

class ExerciseSetSerializer(serializers.ModelSerializer):
    details = SetDetailSerializer(many=True)

    class Meta:
        model = ExerciseSet
        fields = ['exercise_name', 'body_part', 'joint_type', 'sets', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        exercise_set = ExerciseSet.objects.create(**validated_data)
        for detail_data in details_data:
            SetDetail.objects.create(exercise_set=exercise_set, **detail_data)
        return exercise_set

class ExerciseSerializer(serializers.ModelSerializer):
    sets = ExerciseSetSerializer(many=True)
    # exercise_type = ExerciseTypeSerializer(many=True)  # 使用嵌套序列化器顯示詳細資料
    exercise_type = serializers.SlugRelatedField(
        many=True, slug_field="description", queryset=ExerciseType.objects.all()
    )

    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'goal', 'total_duration', 'manual_calories_burned', 
            'calculated_calories_burned', 'scheduled_date', 'created_at', 
            'exercise_type', 'sets'
        ]

    def create(self, validated_data):
        sets_data = validated_data.pop('sets')
        exercise_types_data = validated_data.pop('exercise_type')
        exercise = Exercise.objects.create(**validated_data)
        exercise.exercise_type.set(exercise_types_data)

        for set_data in sets_data:
            details_data = set_data.pop('details')
            exercise_set = ExerciseSet.objects.create(exercise=exercise, **set_data)
            for detail_data in details_data:
                SetDetail.objects.create(exercise_set=exercise_set, **detail_data)

        return exercise

    def update(self, instance, validated_data):
        sets_data = validated_data.pop('sets', None)
        exercise_types_data = validated_data.pop('exercise_type', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if exercise_types_data is not None:
            instance.exercise_type.set(exercise_types_data)

        if sets_data is not None:
            instance.sets.all().delete()
            for set_data in sets_data:
                details_data = set_data.pop('details')
                exercise_set = ExerciseSet.objects.create(exercise=instance, **set_data)
                for detail_data in details_data:
                    SetDetail.objects.create(exercise_set=exercise_set, **detail_data)

        return instance

class TemplateSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'exercises', 'created_at', 'updated_at']

