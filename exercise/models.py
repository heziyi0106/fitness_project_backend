from django.db import models
from django.utils.translation import gettext_lazy as _

class ExerciseType(models.Model):
    """
    運動類型模型，定義不同的運動類別。
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    GOAL_CHOICES = [
        ('muscle_gain', _('Muscle Gain')),
        ('fat_loss', _('Fat Loss')),
        ('endurance', _('Endurance')),
        ('flexibility', _('Flexibility')),
        ('general_fitness', _('General Fitness')),
    ]

    name = models.CharField(max_length=100)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='general_fitness')
    total_duration = models.PositiveIntegerField(help_text="Total duration in minutes")
    # 其他字段
    def __str__(self):
        return self.name

class ExerciseSet(models.Model):
    BODY_PART_CHOICES = [
        ('chest', _('Chest')),
        ('back', _('Back')),
        ('legs', _('Legs')),
        ('shoulders', _('Shoulders')),
        ('arms', _('Arms')),
        ('core', _('Core')),
        ('full_body', _('Full Body')),
    ]
    exercise = models.ForeignKey(Exercise, related_name='sets', on_delete=models.CASCADE)
    exercise_name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=20, choices=BODY_PART_CHOICES, default='full_body')
    sets = models.PositiveIntegerField()
    reps_per_set = models.PositiveIntegerField()
    duration_per_set = models.PositiveIntegerField(help_text="Duration per set in minutes", blank=True, null=True)
    weight = models.PositiveIntegerField(help_text="Weight per rep in kg", blank=True, null=True)

    def total_reps(self):
        """
        計算總次數
        """
        return self.sets * self.reps_per_set

    def total_duration(self):
        """
        計算總時間
        """
        if self.duration_per_set:
            return self.sets * self.duration_per_set
        return None

    def total_volume(self):
        """
        計算總訓練量（組數 * 次數 * 重量）
        """
        if self.weight:
            return self.sets * self.reps_per_set * self.weight
        return self.total_reps()


class Template(models.Model):
    """
    運動範本模型，保存一個運動範本，供未來重複使用。
    """
    name = models.CharField(max_length=100)  # 範本名稱
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)  # 關聯到運動
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template: {self.name}"


# 範本相關邏輯
def save_as_template(exercise_id, template_name):
    """
    將某次運動保存為範本
    """
    exercise = Exercise.objects.get(id=exercise_id)
    template = Template.objects.create(name=template_name, exercise=exercise)
    return template


def create_from_template(template_id):
    """
    基於範本創建新的運動記錄
    """
    template = Template.objects.get(id=template_id)
    new_exercise = Exercise.objects.create(
        name=template.exercise.name,
        total_duration=template.exercise.total_duration,
        goal=template.exercise.goal
    )
    for exercise_set in template.exercise.sets.all():
        ExerciseSet.objects.create(
            exercise=new_exercise,
            exercise_name=exercise_set.exercise_name,
            body_part=exercise_set.body_part,
            sets=exercise_set.sets,
            reps_per_set=exercise_set.reps_per_set,
            duration_per_set=exercise_set.duration_per_set,
            weight=exercise_set.weight
        )
    return new_exercise
