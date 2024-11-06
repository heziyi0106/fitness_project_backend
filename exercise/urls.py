from django.urls import path
from .views import MonthlyPlansView, WeeklyPlansView, BodyCompositionDetailView, CreateExercisePlanView, TemplateListView, TemplateDetailView, CreateFromTemplateView

urlpatterns = [
    path('monthly_plans/', MonthlyPlansView.as_view(), name='monthly-plans'),
    path('weekly_plans/', WeeklyPlansView.as_view(), name='weekly-plans'),    
    path('create_exercise_plan/', CreateExercisePlanView.as_view(), name='create-exercise-plan'),
    path('body_composition/', BodyCompositionDetailView.as_view(), name='body-composition'),
    path('templates/', TemplateListView.as_view(), name='template_list'),
    path('templates/<int:template_id>/', TemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:template_id>/create/', CreateFromTemplateView.as_view(), name='create_from_template'),
]