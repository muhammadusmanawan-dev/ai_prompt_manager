from django.db import models
from django.conf import settings

class AIUsageLog(models.Model):
    ACTION_CHOICES = (
        ('IMPROVE', 'Improve Prompt'),
        ('GENERATE', 'Generate Prompt'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_usage')
    prompt = models.ForeignKey('prompts.Prompt', on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    provider = models.CharField(max_length=50)
    model_used = models.CharField(max_length=50, blank=True, null=True)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.action} via {self.provider}"