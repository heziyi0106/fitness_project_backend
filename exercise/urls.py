from django.urls import path
from .views import MonthlyPlansView, WeeklyPlansView, BodyCompositionDetailView, CreateExercisePlanView

urlpatterns = [
    path('monthly_plans/', MonthlyPlansView.as_view(), name='monthly-plans'),
    path('weekly_plans/', WeeklyPlansView.as_view(), name='weekly-plans'),    
    path('create_exercise_plan/', CreateExercisePlanView.as_view(), name='create-exercise-plan'),
    path('body_composition/', BodyCompositionDetailView.as_view(), name='body-composition'),
]
