from django.db import models
from django.utils.translation import gettext_lazy as _

class BodyComposition(models.Model):
    """
    身體組成數據
    """

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # 假設會關聯到使用者模型
    weight = models.FloatField(help_text="體重（公斤）", default=0.0)
    body_fat_percentage = models.FloatField(help_text="體脂率（百分比）", default=0.0)
    muscle_mass = models.FloatField(help_text="肌肉量（公斤）", default=0.0)
    bmi = models.FloatField(help_text="身體質量指數", default=0.0)
    visceral_fat = models.FloatField(help_text="內臟脂肪等級", default=0.0)
    waist_circumference = models.FloatField(help_text="腰圍（公分）", default=0.0)
    hip_circumference = models.FloatField(help_text="臀圍（公分）", default=0.0)

    measured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Body Composition for {self.user.username} at {self.measured_at}"

class ExerciseType(models.Model):
    """
    運動類型模型，定義不同的運動類別。
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    """
    記載每次建立的運動計劃，包含本次運動的名稱（如早上健身）、運動的目標、運動總時間、運動類型（有氧、重訓或複合式）
    """
    # 運動目標
    GOAL_CHOICES = [
        ('muscle_gain', _('Muscle Gain')),
        ('fat_loss', _('Fat Loss')),
        ('endurance', _('Endurance')),
        ('flexibility', _('Flexibility')),
        ('general_fitness', _('General Fitness')),
    ]

    name = models.CharField(max_length=100)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='general_fitness')
    total_duration = models.PositiveIntegerField(help_text="Total duration in minutes", default=0)
    # 將 ForeignKey 改為 ManyToManyField 以支持多個運動類型
    exercise_type = models.ManyToManyField(ExerciseType, blank=True)

    def __str__(self):
        return self.name
    
    def update_total_duration(self):
        """
        計算所有 ExerciseSet 的總時間，並將結果保存到 total_duration 欄位
        """
        # 計算所有相關的 ExerciseSet 的總時間，並將秒數轉換為分鐘
        total_seconds = sum([exercise_set.total_duration() for exercise_set in self.sets.all()])
        self.total_duration = total_seconds // 60  # 將秒數轉換為分鐘
        self.save()  # 保存更新到資料庫

class ExerciseSet(models.Model):
    """
    每個運動計劃中的詳細內容：包含運動計劃名稱、動作項目的名稱、訓練部位、動作參與關節類型、訓練組數、每組反覆次數、每組持續時間、每組訓練重量
    """
    # 訓練部位
    BODY_PART_CHOICES = [
        ('chest', _('Chest')),
        ('back', _('Back')),
        ('legs', _('Legs')),
        ('shoulders', _('Shoulders')),
        ('arms', _('Arms')),
        ('core', _('Core')),
        ('full_body', _('Full Body')),
    ]

    # 動作參與關節類型
    JOINT_TYPE_CHOICES = [
        ('single_joint', _('Single Joint')),
        ('multi_joint', _('Multi Joint')),
    ]

    exercise = models.ForeignKey(Exercise, related_name='sets', on_delete=models.CASCADE)
    exercise_name = models.CharField(max_length=100)
    body_part = models.CharField(max_length=20, choices=BODY_PART_CHOICES, default='full_body')
    joint_type = models.CharField(max_length=20, choices=JOINT_TYPE_CHOICES, default='multi_joint')
    sets = models.PositiveIntegerField()

    def total_duration(self):
        """
        計算該動作的總訓練時間，將所有 SetDetail 的時間加總
        """
        return sum([detail.calculate_time() for detail in self.details.all()])
    
    def save(self, *args, **kwargs):
        """
        每當保存這個 ExerciseSet 時，都會更新 Exercise 的總時間
        """
        super().save(*args, **kwargs)
        # 在保存每個 ExerciseSet 之後，更新 Exercise 的總時間
        self.exercise.update_total_duration()

class SetDetail(models.Model):
    """
    記錄每一組的實際反覆次數、訓練重量、每組持續時間和每組之間的休息時間。
    """
    exercise_set = models.ForeignKey(ExerciseSet, related_name='details', on_delete=models.CASCADE)
    reps = models.PositiveIntegerField()  # 每組實際的反覆次數
    weight = models.FloatField()  # 每組實際的訓練重量（以 kg 計算）
    actual_duration = models.PositiveIntegerField(help_text="Actual duration per set in seconds")  # 每組實際做的時間，以秒為單位
    rest_time = models.PositiveIntegerField(help_text="Rest time between sets in seconds")  # 每組之間的休息時間，以秒為單位

    def __str__(self):
        return f"{self.reps} reps @ {self.weight} kg, {self.actual_duration}s work, {self.rest_time}s rest"
    
    def calculate_volume(self):
        """
        計算該組的訓練總量，只有反覆次數在 3～15 之間的組會計入總量
        """
        if 3 <= self.reps <= 15:
            return self.reps * self.weight
        return 0  # 不符合條件的不計算訓練總量

    def calculate_time(self):
        """
        計算該組的總時間（實際訓練時間 + 休息時間）
        """
        return self.actual_duration + self.rest_time

class Template(models.Model):
    """
    運動範本模型，保存一個範本，供未來重複使用，範本可以包含多個運動。
    """
    name = models.CharField(max_length=100)  # 範本名稱
    exercises = models.ManyToManyField(Exercise)  # 一個範本可以包含多個 Exercise
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Template: {self.name}"

# 範本相關邏輯
def save_as_template(exercise_ids, template_name):
    """
    將多個運動保存為範本
    """
    template = Template.objects.create(name=template_name)
    
    # 將多個運動添加到範本中
    exercises = Exercise.objects.filter(id__in=exercise_ids)
    template.exercises.set(exercises)
    
    return template

def create_from_template(template_id):
    """
    基於範本創建新的運動記錄
    """
    template = Template.objects.get(id=template_id)
    
    new_exercises = []
    
    # 複製範本中的每個運動
    for exercise in template.exercises.all():
        new_exercise = Exercise.objects.create(
            name=exercise.name,
            total_duration=exercise.total_duration,
            goal=exercise.goal,
            exercise_type=exercise.exercise_type
        )
        
        # 複製每個 ExerciseSet
        for exercise_set in exercise.sets.all():
            new_exercise_set = ExerciseSet.objects.create(
                exercise=new_exercise,
                exercise_name=exercise_set.exercise_name,
                body_part=exercise_set.body_part,
                joint_type=exercise_set.joint_type,
                sets=exercise_set.sets
            )
            
            # 複製每個 ExerciseSet 相關的 SetDetail
            for detail in exercise_set.details.all():
                SetDetail.objects.create(
                    exercise_set=new_exercise_set,
                    reps=detail.reps,
                    weight=detail.weight,
                    actual_duration=detail.actual_duration,
                    rest_time=detail.rest_time
                )
        
        new_exercises.append(new_exercise)
    
    return new_exercises

def duplicate_template(template_id, new_template_name):
    """
    複製範本，並儲存成另一個名字
    """
    # 取得原範本
    original_template = Template.objects.get(id=template_id)
    
    # 創建新的範本
    new_template = Template.objects.create(name=new_template_name)
    
    # 將原範本中的所有 Exercise 關聯到新範本
    new_template.exercises.set(original_template.exercises.all())
    
    return new_template
