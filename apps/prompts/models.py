import uuid
from django.db import models
from django.conf import settings
 
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Prompt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prompts')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='category_prompts'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content = models.TextField()
    is_public = models.BooleanField(default=False)
    current_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = "Prompts"

    def __str__(self):
        return f"{self.title} (v{self.current_version})"


class PromptHistory(models.Model):
    prompt = models.ForeignKey(
        Prompt, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    change_description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['prompt', 'version_number'], 
                name='unique_prompt_version'
            )
        ]

    def __str__(self):
        return f"{self.prompt.title} - Version {self.version_number}"
    