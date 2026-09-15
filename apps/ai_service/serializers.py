from rest_framework import serializers

class ImprovePromptSerializer(serializers.Serializer):
    prompt_content = serializers.CharField(required=True)
    instructions = serializers.CharField(required=False, allow_blank=True, default="")
    provider = serializers.CharField(required=False, default="openai")

class GeneratePromptSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    provider = serializers.CharField(required=False, default="openai")