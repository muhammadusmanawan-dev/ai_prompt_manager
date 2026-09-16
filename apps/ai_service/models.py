import uuid
from django.db import models
from django.conf import settings


class AIExecutionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='ai_logs'
    )
    provider = models.CharField(max_length=50)  # e.g., 'openai', 'anthropic'
    action_type = models.CharField(max_length=50)  # e.g., 'improve', 'generate'
    input_text = models.TextField()
    output_text = models.TextField(blank=True, null=True)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.action_type} via {self.provider} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
