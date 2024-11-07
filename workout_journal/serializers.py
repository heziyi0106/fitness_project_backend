from rest_framework import serializers
from .models import WorkoutJournalEntry

class WorkoutJournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutJournalEntry
        fields = '__all__'
