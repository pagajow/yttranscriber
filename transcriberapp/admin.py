from django.contrib import admin
from .models import AsyncTask, AsyncTaskLog, Transcription

class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ("url", "language", "title", "duration", "created_at")
    search_fields = ("title", "url")
    ordering = ("-created_at",)

class AsyncTaskAdmin(admin.ModelAdmin):
    list_display = ("task_id", "task_type", "status", "created_at")
    list_filter = ("status", "task_type")
    search_fields = ("task_id",)
    ordering = ("-created_at",)

class AsyncTaskLogAdmin(admin.ModelAdmin):
    list_display = ("task_id", "status", "message", "created_at")
    readonly_fields = ("task", "status", "message", "created_at")
    ordering = ("-created_at",)
    
    def task_id(self, obj):
        return obj.task.task_id 
    
    task_id.short_description = "Task ID"
    task_id.admin_order_field = "task__task_id"

    def has_change_permission(self, request, obj=None):
        return False
    
    


admin.site.register(Transcription, TranscriptionAdmin)
admin.site.register(AsyncTask, AsyncTaskAdmin)
admin.site.register(AsyncTaskLog, AsyncTaskLogAdmin)
