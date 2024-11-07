from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import WorkoutJournalEntry
from .serializers import WorkoutJournalEntrySerializer

class WorkoutJournalEntryViewSet(viewsets.ModelViewSet):
    queryset = WorkoutJournalEntry.objects.all()
    serializer_class = WorkoutJournalEntrySerializer
    permission_classes = [IsAuthenticated]