from django.contrib import admin
from .models import Exercise

# 註冊 Exercise 模型
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_duration', 'goal')  # 設定管理界面中顯示的字段
