from django.db import transaction
from .models import Prompt, PromptHistory

class PromptService:

    @staticmethod
    @transaction.atomic
    def create_prompt(user, validated_data):
        prompt = Prompt.objects.create(user=user, **validated_data)
        PromptHistory.objects.create(
            prompt=prompt,
            version_number=1,
            title=prompt.title,
            content=prompt.content,
            change_description="Initial creation"
        )
        return prompt

    @staticmethod
    @transaction.atomic
    def update_prompt(prompt, validated_data, change_description="Updated prompt details"):
        content_changed = 'content' in validated_data and validated_data['content'] != prompt.content
        title_changed = 'title' in validated_data and validated_data['title'] != prompt.title

        for key, value in validated_data.items():
            setattr(prompt, key, value)

        if content_changed or title_changed:
            prompt.current_version += 1
            PromptHistory.objects.create(
                prompt=prompt,
                version_number=prompt.current_version,
                title=prompt.title,
                content=prompt.content,
                change_description=change_description
            )

        prompt.save()
        return prompt