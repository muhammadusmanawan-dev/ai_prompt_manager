from rest_framework import serializers
from .models import Category, Prompt, PromptHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class PromptSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Prompt
        fields = [
            'id', 'user', 'category', 'title', 
            'description', 'content', 'is_public', 
            'current_version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'current_version', 'created_at', 'updated_at']


class PromptHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptHistory
        fields = [
            'id', 'prompt', 'version_number', 
            'title', 'content', 'change_description', 'created_at'
        ]
        read_only_fields = ['id', 'prompt', 'version_number', 'title', 'content', 'change_description', 'created_at']