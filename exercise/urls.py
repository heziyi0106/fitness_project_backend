from django.urls import path
from .views import (
    ExerciseTypeListCreateView, ExerciseListCreateView, ExerciseDetailView,
    ExerciseSetListCreateView, ExerciseSetDetailView, SetDetailListCreateView, SetDetailDetailView,
    TemplateListCreateView, TemplateDetailView, CreateExerciseFromTemplateView, DuplicateTemplateView
)

urlpatterns = [
    path('exercise_types/', ExerciseTypeListCreateView.as_view(), name='exercise_type_list_create'),
    path('exercises/', ExerciseListCreateView.as_view(), name='exercise_list_create'),
    path('exercises/<int:pk>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercise_sets/', ExerciseSetListCreateView.as_view(), name='exercise_set_list_create'),
    path('exercise_sets/<int:pk>/', ExerciseSetDetailView.as_view(), name='exercise_set_detail'),
    path('set_details/', SetDetailListCreateView.as_view(), name='set_detail_list_create'),
    path('set_details/<int:pk>/', SetDetailDetailView.as_view(), name='set_detail_detail'),
    path('templates/', TemplateListCreateView.as_view(), name='template_list_create'),
    path('templates/<int:pk>/', TemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:template_id>/create_exercise/', CreateExerciseFromTemplateView.as_view(), name='create_exercise_from_template'),
    path('templates/<int:template_id>/duplicate/', DuplicateTemplateView.as_view(), name='duplicate_template'),
]
