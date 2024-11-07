from django.db import models

class WorkoutJournalEntry(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()  # Using TinyMCE for rich text editing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title