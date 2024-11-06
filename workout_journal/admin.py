from django.contrib import admin
from .models import WorkoutJournalEntry

# Register your models here.
@admin.register(WorkoutJournalEntry)
class WorkoutJournalEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')