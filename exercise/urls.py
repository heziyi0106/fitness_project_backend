from django.urls import path
from .views import MonthlyPlansView, WeeklyPlansView

urlpatterns = [
    path('monthly_plans/', MonthlyPlansView.as_view(), name='monthly-plans'),
    path('weekly_plans/', WeeklyPlansView.as_view(), name='weekly-plans'),  # 新增這個路由
]
