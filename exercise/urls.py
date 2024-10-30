from django.urls import path
from .views import MonthlyPlansView, WeeklyPlansView, BodyCompositionView

urlpatterns = [
    path('monthly_plans/', MonthlyPlansView.as_view(), name='monthly-plans'),
    path('weekly_plans/', WeeklyPlansView.as_view(), name='weekly-plans'),
    path('body_composition/', BodyCompositionView.as_view(), name='body-composition'),
]
