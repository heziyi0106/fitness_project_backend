from django.db import models
from tinymce.models import HTMLField
# Create your models here.

class WorkoutJournalEntry(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()  # Using TinyMCE for rich text editing
    image = models.ImageField(upload_to='workout_journal_images/', blank=True, null=True)  # Image field for storing uploaded images
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title