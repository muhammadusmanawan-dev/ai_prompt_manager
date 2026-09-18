from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Prompt, PromptHistory
from .permissions import IsOwnerOrPublicReadOnly
from .serializers import (
    CategorySerializer,
    PromptHistorySerializer,
    PromptSerializer,
)

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PromptViewSet(viewsets.ModelViewSet):
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrPublicReadOnly]

    search_fields = ['title', 'description', 'content']
    filterset_fields = ['category', 'is_public', 'user']

    def get_queryset(self):
        return (
            Prompt.objects.filter(is_public=True)| Prompt.objects.filter(user=self.request.user)
        )

    @transaction.atomic
    def perform_create(self, serializer):
        prompt = serializer.save(
            user=self.request.user,
            current_version=1
        )

        PromptHistory.objects.create(
            prompt=prompt,
            version_number=1,
            title=prompt.title,
            content=prompt.content,
            change_description="Initial draft created."
        )

    @transaction.atomic
    def perform_update(self, serializer):
        prompt = serializer.instance
        title_changed = (
            'title' in serializer.validated_data and serializer.validated_data['title'] != prompt.title
        )
        content_changed = (
            'content' in serializer.validated_data and serializer.validated_data['content'] != prompt.content
        )
        prompt = serializer.save()
        
        if title_changed or content_changed:
            prompt.current_version +=1
            prompt.save(update_fields=['current_version', 'updated_at'])

            PromptHistory.objects.create(
                prompt=prompt,
                version_number=prompt.current_version,
                title=prompt.title,
                content=prompt.content,
                change_description=(
                    f"Updated to version {prompt.current_version}"
                )
            )

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        prompt = self.get_object()
        history = prompt.history.all()
        serializer = PromptHistorySerializer(history,many=True)
        return Response(serializer.data)