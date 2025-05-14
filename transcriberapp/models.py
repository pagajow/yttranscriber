from django.db import models

# Create your models here.
class Transcription(models.Model):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("pl", "Polski"),
        ("de", "Deutsch"),
        ("fr", "Français"),
        ("es", "Español"),
    ]
    
    url = models.URLField(max_length=255)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, blank=False)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Transcription for {self.url} in {self.language}"