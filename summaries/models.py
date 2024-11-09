from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Summary(models.Model):    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True  # Add this to allow null temporarily for migration
    )
    youtube_url = models.URLField(max_length=500, blank=True)  # Changed to URLField
    summary = models.TextField(blank=True)  # Remove default, use blank=True
    timestamps = models.TextField(blank=True)  # Remove default, use blank=True
    youtube_transcript = models.TextField(blank=True)  # Remove default, use blank=True
    date_generated = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.youtube_url}"
    
class Feedback(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True  # Add this to allow null temporarily for migration
    )
    username = models.CharField(max_length=255, blank=True)
    email_id = models.EmailField(max_length=255, blank=True)  # Changed to EmailField
    feedback = models.TextField()
    date_generated = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date_generated}"