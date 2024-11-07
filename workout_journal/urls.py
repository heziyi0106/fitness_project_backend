from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutJournalEntryViewSet
router = DefaultRouter()
router.register(r'workout-journals', WorkoutJournalEntryViewSet, basename='workoutjournal')

urlpatterns = [
    path('', include(router.urls)),
]