from rest_framework import serializers
from .models import BodyComposition, Exercise, ExerciseSet, SetDetail, ExerciseType, Template
from django.utils.translation import gettext_lazy as _

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

    def create(self, validated_data):
        if validated_data.get('height') > 0:
            validated_data['bmi'] = validated_data['weight'] / ((validated_data['height'] / 100) ** 2)
        else:
            validated_data['bmi'] = 0.0
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('height', instance.height) > 0:
            validated_data['bmi'] = validated_data.get('weight', instance.weight) / ((validated_data.get('height', instance.height) / 100) ** 2)
        else:
            validated_data['bmi'] = 0.0
        return super().update(instance, validated_data)

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
    body_part = serializers.IntegerField()  # 接收數字值
    joint_type = serializers.IntegerField()  # 接收數字值

    class Meta:
        model = ExerciseSet
        fields = ['exercise_name', 'body_part', 'joint_type', 'sets', 'details']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 使用字典來將 body_part 和 joint_type 的數字轉換成對應的描述
        representation['body_part'] = ExerciseSet.BODY_PART_CHOICES.get(instance.body_part, _('Unknown'))
        representation['joint_type'] = ExerciseSet.JOINT_TYPE_CHOICES.get(instance.joint_type, _('Unknown'))
        return representation

    # 這裡新增一個 create 方法
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        sets = validated_data.get('sets')
        
        # 檢查 details 的數量是否和 sets 一致
        if len(details_data) != sets:
            raise serializers.ValidationError(f"Details 的數量應該等於 sets 的數量 ({sets})。")
        
        exercise_set = ExerciseSet.objects.create(**validated_data)
        
        for detail_data in details_data:
            SetDetail.objects.create(exercise_set=exercise_set, **detail_data)
        
        return exercise_set

class ExerciseSerializer(serializers.ModelSerializer):
    sets = ExerciseSetSerializer(many=True)
    goal = serializers.IntegerField()  # 直接接收數字
    # exercise_type = ExerciseTypeSerializer(many=True)  # 使用嵌套序列化器顯示詳細資料
    exercise_type = serializers.PrimaryKeyRelatedField(queryset=ExerciseType.objects.all(), many=True)

    class Meta:
        model = Exercise
        fields = [
            'id', 'name', 'goal', 'total_duration', 'manual_calories_burned', 
            'calculated_calories_burned', 'scheduled_date', 'created_at', 
            'exercise_type', 'sets'
        ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 將數字目標轉換為文字
        representation['goal'] = Exercise.GOAL_CHOICES.get(instance.goal, _('Unknown'))
        return representation

    def create(self, validated_data):
        sets_data = validated_data.pop('sets')
        exercise_types_data = validated_data.pop('exercise_type')  # 這裡是 ID 列表
        exercise = Exercise.objects.create(**validated_data)
        exercise.exercise_type.set(exercise_types_data)

        for set_data in sets_data:
            details_data = set_data.pop('details')
            # 先創建 ExerciseSet
            exercise_set = ExerciseSet.objects.create(exercise=exercise, **set_data)
            # 創建 SetDetail
            for detail_data in details_data:
                SetDetail.objects.create(exercise_set=exercise_set, **detail_data)
            # 更新 sets 的值為 details 的數量
            exercise_set.sets = len(details_data)
            exercise_set.save()

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
                # 更新 sets 為 details 的數量
                set_data['sets'] = len(details_data)
                exercise_set = ExerciseSet.objects.create(exercise=instance, **set_data)
                for detail_data in details_data:
                    SetDetail.objects.create(exercise_set=exercise_set, **detail_data)

        return instance


class TemplateSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'exercises', 'created_at', 'updated_at']

