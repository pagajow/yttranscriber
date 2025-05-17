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
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=512, null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    thumbnail = models.URLField(max_length=255, null=True, blank=True)
    text = models.TextField(blank=True, default="")
    summary = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Transcription for {self.url} in {self.language}"
    

class AsyncTask(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    TASK_TYPE_CHOSCES = [
        ("transcription", "Transcription"),
        ("ai_request", "AI Request"),
    ]   
    transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, null=False, blank=False, related_name="tasks")
    task_id = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOSCES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task {self.task_id} - {self.status}"
    
    @property
    def is_done(self):
        return self.status in ["completed", "failed"]

class AsyncTaskLog(models.Model):
    task = models.ForeignKey(AsyncTask, on_delete=models.CASCADE, related_name="logs")
    message = models.TextField()
    status = models.CharField(max_length=20, choices=AsyncTask.STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task log {self.created_at}: ({self.task.task_id}) - {self.message})"
    
    def save(self, *args, **kwargs):
        if self.pk and AsyncTaskLog.objects.filter(pk=self.pk).exists():
            raise ValueError("Editing task logs is not allowed.")
        super().save(*args, **kwargs)
        self.task.status = self.status
        self.task.save()