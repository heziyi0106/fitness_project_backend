from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class BodyComposition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    height = models.FloatField(help_text="身高（公分）", default=0.0)
    weight = models.FloatField(help_text="體重（公斤）", default=0.0)
    body_fat_percentage = models.FloatField(help_text="體脂率（百分比）", default=0.0)
    muscle_mass = models.FloatField(help_text="肌肉量（公斤）", default=0.0)
    bmi = models.FloatField(help_text="身體質量指數", default=0.0, null=True, blank=True)
    visceral_fat = models.FloatField(help_text="內臟脂肪等級", default=0.0)
    basal_metabolic_rate = models.IntegerField(help_text="基礎代謝率 (kcal/day)", blank=True, null=True)
    waist_circumference = models.FloatField(help_text="腰圍（公分）", default=0.0)
    hip_circumference = models.FloatField(help_text="臀圍（公分）", default=0.0)
    chest_circumference = models.FloatField(help_text="胸圍（公分）", default=0.0)
    shoulder_circumference = models.FloatField(help_text="肩围 (cm)", null=True, blank=True)
    upper_arm_circumference = models.FloatField(help_text="上臂圍 (公分)", null=True, blank=True)
    lower_arm_circumference = models.FloatField(help_text="下臂圍 (公分)", null=True, blank=True)
    thigh_circumference = models.FloatField(help_text="大腿圍 (公分)", null=True, blank=True)
    calf_circumference = models.FloatField(help_text="小腿圍 (公分)", null=True, blank=True)
    measured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Body Composition for {self.user.username} at {self.measured_at}"

    def clean(self):
        if not (0 < self.height <= 250):
            raise ValidationError("身高數值不合理，應該在 0cm 到 250cm 之間。")
        if not (0 < self.weight <= 300):
            raise ValidationError("體重數值不合理，應該在 0kg 到 300kg 之間。")
        super().clean()

    @property
    def calculate_bmi(self):
        if self.height > 0:
            return self.weight / ((self.height / 100) ** 2)
        return 0.0

class ExerciseType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    GOAL_CHOICES = {
        1: _('Muscle Gain'),
        2: _('Fat Loss'),
        3: _('Endurance'),
        4: _('Flexibility'),
        5: _('General Fitness'),
    }    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    goal = models.IntegerField(choices=list(GOAL_CHOICES.items()), default=5)
    total_duration = models.PositiveIntegerField(help_text="運動總時間", default=0)    
    exercise_type = models.ManyToManyField(ExerciseType, blank=True)
    manual_calories_burned = models.FloatField(help_text="手動輸入的熱量消耗（大卡）", null=True, blank=True)
    calculated_calories_burned = models.FloatField(help_text="自動計算的熱量消耗（大卡）", default=0.0)
    scheduled_date = models.DateField(help_text="運動計劃的安排日期")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.scheduled_date}"
    
    def update_total_duration(self):
        """
        計算所有 ExerciseSet 的總時間，並將結果保存到 total_duration 欄位
        """
        # 呼叫 total_duration 方法，注意加上 ()
        total_seconds = sum(exercise_set.total_duration() for exercise_set in self.sets.all())
        self.total_duration = total_seconds // 60  # 將秒數轉換為分鐘
        self.save()  # 保存更新到資料庫
    
    @property
    def get_goal_display(self):
        return self.GOAL_CHOICES.get(self.goal, _('Unknown'))

    @property
    def get_met_value(self):
        met_values = {
            '重量訓練': 6.0, '有氧運動': 8.0,
            '核心訓練': 5.0, '柔韌性訓練': 3.0, '平衡訓練': 2.5,
        }
        return sum(met_values.get(type.name, 8.0) for type in self.exercise_type.all()) / self.exercise_type.count()

    def calculate_calories(self, weight):
        calories_per_minute = self.get_met_value * weight * 3.5 / 200
        total_calories = calories_per_minute * self.total_duration
        self.calculated_calories_burned = total_calories
        return total_calories

    @property
    def get_calories_burned(self):
        return self.manual_calories_burned or self.calculated_calories_burned

class ExerciseSet(models.Model):
    BODY_PART_CHOICES = {
        1: _('Chest'),
        2: _('Back'),
        3: _('Legs'),
        4: _('Shoulders'),
        5: _('Arms'),
        6: _('Core'),
        7: _('Full Body'),
    }

    JOINT_TYPE_CHOICES = {
        1: _('Single Joint'),
        2: _('Multi Joint'),
    }
    exercise = models.ForeignKey(Exercise, related_name='sets', on_delete=models.CASCADE)
    exercise_name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=20, choices=list(BODY_PART_CHOICES.items()), default=7)
    joint_type = models.CharField(max_length=20, choices=list(JOINT_TYPE_CHOICES.items()), default=2)
    sets = models.PositiveIntegerField()

    def total_duration(self):
        return sum(detail.calculate_time for detail in self.details.all())
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.exercise.update_total_duration()

class SetDetail(models.Model):
    exercise_set = models.ForeignKey(ExerciseSet, related_name='details', on_delete=models.CASCADE)
    reps = models.PositiveIntegerField()
    weight = models.FloatField()
    actual_duration = models.PositiveIntegerField(help_text="Actual duration per set in seconds")
    rest_time = models.PositiveIntegerField(help_text="Rest time between sets in seconds")

    def __str__(self):
        return f"{self.reps} reps @ {self.weight} kg, {self.actual_duration}s work, {self.rest_time}s rest"
    
    @property
    def calculate_volume(self):
        return self.reps * self.weight if 3 <= self.reps <= 15 else 0

    @property
    def calculate_time(self):
        return self.actual_duration + self.rest_time

class Template(models.Model):
    name = models.CharField(max_length=100)
    exercises = models.ManyToManyField(Exercise)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template: {self.name}"

def save_as_template(exercise_ids, template_name):
    template = Template.objects.create(name=template_name)
    template.exercises.set(Exercise.objects.filter(id__in=exercise_ids).select_related('user'))
    return template

def create_from_template(template_id):
    template = Template.objects.prefetch_related('exercises__sets__details').get(id=template_id)
    new_exercises = []
    for exercise in template.exercises.all():
        new_exercise = Exercise.objects.create(
            name=exercise.name, total_duration=exercise.total_duration, goal=exercise.goal
        )
        for exercise_set in exercise.sets.all():
            new_exercise_set = ExerciseSet.objects.create(
                exercise=new_exercise, exercise_name=exercise_set.exercise_name, body_part=exercise_set.body_part
            )
            SetDetail.objects.bulk_create([
                SetDetail(exercise_set=new_exercise_set, reps=detail.reps, weight=detail.weight, actual_duration=detail.actual_duration)
                for detail in exercise_set.details.all()
            ])
        new_exercises.append(new_exercise)
    return new_exercises
