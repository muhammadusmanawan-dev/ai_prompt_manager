from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Prompt
from .permissions import IsOwnerOrPublicReadOnly
from .serializers import CategorySerializer, PromptHistorySerializer, PromptSerializer
from .services import PromptService


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	permission_classes = [IsAuthenticated]


class PromptViewSet(viewsets.ModelViewSet):
	serializer_class = PromptSerializer
	permission_classes = [IsAuthenticated, IsOwnerOrPublicReadOnly]
	search_fields = ['title', 'description', 'content']
	filterset_fields = ['category', 'is_public', 'user']

	def get_queryset(self):
		return Prompt.objects.filter(is_public=True) | Prompt.objects.filter(user=self.request.user)

	def perform_create(self, serializer):
		validated_data = serializer.validated_data
		serializer.instance = PromptService.create_prompt(user=self.request.user, **validated_data)

	def update(self, request, *args, **kwargs):
		prompt = self.get_object()
		serializer = self.get_serializer(prompt, data=request.data, partial=kwargs.pop('partial', False))
		serializer.is_valid(raise_exception=True)
		PromptService.update_prompt(prompt, **serializer.validated_data)
		return Response(self.get_serializer(prompt).data)

	@action(detail=True, methods=['get'], url_path='history')
	def history(self, request, pk=None):
		prompt = self.get_object()
		serializer = PromptHistorySerializer(prompt.history.all(), many=True)
		return Response(serializer.data)
