from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class BodyComposition(models.Model):
    """
    身體組成數據
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 假設會關聯到使用者模型
    # 體重器可以測
    height = models.FloatField(help_text="身高（公分）", default=0.0)
    weight = models.FloatField(help_text="體重（公斤）", default=0.0)
    body_fat_percentage = models.FloatField(help_text="體脂率（百分比）", default=0.0)
    muscle_mass = models.FloatField(help_text="肌肉量（公斤）", default=0.0)
    bmi = models.FloatField(help_text="身體質量指數", default=0.0, null=True, blank=True)
    visceral_fat = models.FloatField(help_text="內臟脂肪等級", default=0.0)
    basal_metabolic_rate = models.IntegerField(help_text="基礎代謝率 (kcal/day)", blank=True, null=True)
    # 身體圍度 
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
        """
        自定義驗證，確保身高和體重的合理範圍
        """
        if self.height <= 0 or self.height > 250:
            raise ValidationError("身高數值不合理，應該在 0cm 到 250cm 之間。")
        if self.weight <= 0 or self.weight > 300:
            raise ValidationError("體重數值不合理，應該在 0kg 到 300kg 之間。")
        
        # 确保在调用 save() 前执行 clean()
        super().clean()

    def calculate_bmi(self):
        """
        根據體重和身高計算 BMI，需從使用者數據中獲取身高
        """
        self.bmi = self.weight / ((self.height / 100) ** 2)  # 身高轉換為公尺來計算 BMI
        return self.bmi

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='綜合健身')
    total_duration = models.PositiveIntegerField(help_text="運動總時間", default=0)    
    exercise_type = models.ManyToManyField(ExerciseType, blank=True)
    # 新增欄位，儲存由使用者手動輸入的卡路里消耗
    manual_calories_burned = models.FloatField(help_text="手動輸入的熱量消耗（大卡）", null=True, blank=True)
    # 自動計算的卡路里消耗
    calculated_calories_burned = models.FloatField(help_text="自動計算的熱量消耗（大卡）", default=0.0)
    scheduled_date = models.DateField(help_text="運動計劃的安排日期")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.scheduled_date}"
    
    def update_total_duration(self):
        """
        計算所有 ExerciseSet 的總時間，並將結果保存到 total_duration 欄位
        """
        # 計算所有相關的 ExerciseSet 的總時間，並將秒數轉換為分鐘
        total_seconds = sum([exercise_set.total_duration() for exercise_set in self.sets.all()])
        self.total_duration = total_seconds // 60  # 將秒數轉換為分鐘
        self.save()  # 保存更新到資料庫

    def get_met_value(self):
        """
        根據不同的運動類型設置不同的 MET 值
        """
        met_values = {
            '力量訓練': 6.0,
            '有氧運動': 8.0,
            '核心訓練': 5.0,
            '柔韌性訓練': 3.0,
            '平衡訓練': 2.5,
        }
        met_sum = 0
        type_count = self.exercise_type.count()
        for ex_type in self.exercise_type.all():
            met_sum += met_values.get(ex_type.name, 8.0)  # 默認為 8.0
        return met_sum / type_count if type_count > 0 else 8.0

    def calculate_calories(self, weight):
        """
        根據運動的類型、時間和使用者的體重計算總熱量消耗
        """
        met_value = self.get_met_value()  # 取得根據運動類型計算的 MET 值
        calories_per_minute = met_value * weight * 3.5 / 200
        total_calories = calories_per_minute * self.total_duration
        self.calculated_calories_burned = total_calories
        return total_calories

    def get_calories_burned(self):
        """
        返回最終的熱量消耗，優先使用手動輸入的數值，否則使用自動計算的值
        """
        if self.manual_calories_burned is not None:
            return self.manual_calories_burned
        return self.calculated_calories_burned

    def calculate_weight_loss(self):
        """
        根據消耗的熱量來計算可以減少的體重（每消耗 7700 大卡減少 1 公斤）
        """
        total_calories_burned = self.get_calories_burned()
        if total_calories_burned > 0:
            return total_calories_burned / 7700
        return 0

    def save(self, *args, **kwargs):
        # 在保存之前根據使用者的體重計算熱量消耗
        if self.manual_calories_burned is None:  # 只有在用戶未手動輸入時才進行計算
            user_weight = self.user.bodycomposition.weight  # 假設從關聯的使用者模型中取得體重
            self.calculate_calories(user_weight)
        super().save(*args, **kwargs)

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
