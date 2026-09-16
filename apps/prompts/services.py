from django.db import transaction
from .models import Prompt, PromptHistory


class PromptService:
    @staticmethod
    @transaction.atomic
    def create_prompt(user, category, title, description, content, is_public=False):
        prompt = Prompt.objects.create(
            user=user,
            category=category,
            title=title,
            description=description,
            content=content,
            is_public=is_public,
            current_version=1
        )

        PromptHistory.objects.create(
            prompt=prompt,
            version_number=1,
            title=title,
            content=content,
            change_description="Initial draft created."
        )

        return prompt

    @staticmethod
    @transaction.atomic
    def update_prompt(prompt, category=None, title=None, description=None, content=None, is_public=None, change_description=""):
        content_changed = content is not None and content != prompt.content
        title_changed = title is not None and title != prompt.title

        if title is not None:
            prompt.title = title
        if category is not None:
            prompt.category = category
        if description is not None:
            prompt.description = description
        if content is not None:
            prompt.content = content
        if is_public is not None:
            prompt.is_public = is_public

        # Increment version only if title or core content modified
        if content_changed or title_changed:
            prompt.current_version += 1
            PromptHistory.objects.create(
                prompt=prompt,
                version_number=prompt.current_version,
                title=prompt.title,
                content=prompt.content,
                change_description=change_description or f"Updated to version {prompt.current_version}"
            )

        prompt.save()
        return prompt