from django.db.models import Count, Q, Sum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AIExecutionLog
from .providers.factory import AIProviderFactory
from .serializers import GeneratePromptSerializer, ImprovePromptSerializer


def record_execution(
    user,
    provider,
    action_type,
    input_text,
    output_text=None,
    tokens_used=0
):
    AIExecutionLog.objects.create(
        user=user,
        provider=provider,
        action_type=action_type,
        input_text=input_text,
        output_text=output_text,
        tokens_used=tokens_used,
    )


def get_tokens(metadata):
    return (
        metadata.get('prompt_tokens', 0)
        + metadata.get('completion_tokens', 0)
    )


class AIImproveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ImprovePromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        provider_name = data['provider']

        try:
            provider = AIProviderFactory.get_provider(provider_name)

            result, metadata = provider.improve_prompt(
                data['prompt_content'],
                data['instructions']
            )

            record_execution(
                request.user,
                provider_name,
                'improve',
                data['prompt_content'],
                result,
                get_tokens(metadata)
            )

            return Response({
                'result': result,
                'metadata': metadata
            })

        except ValueError as error:
            record_execution(
                request.user,
                provider_name,
                'improve',
                data['prompt_content']
            )

            return Response(
                {'detail': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            record_execution(
                request.user,
                provider_name,
                'improve',
                data['prompt_content']
            )

            return Response(
                {'detail': 'The AI provider request failed.'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class AIGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GeneratePromptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        provider_name = data['provider']

        try:
            provider = AIProviderFactory.get_provider(provider_name)

            result, metadata = provider.generate_prompt(
                data['description']
            )

            record_execution(
                request.user,
                provider_name,
                'generate',
                data['description'],
                result,
                get_tokens(metadata)
            )

            return Response({
                'result': result,
                'metadata': metadata
            })

        except ValueError as error:
            record_execution(
                request.user,
                provider_name,
                'generate',
                data['description']
            )

            return Response(
                {'detail': str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            record_execution(
                request.user,
                provider_name,
                'generate',
                data['description']
            )

            return Response(
                {'detail': 'The AI provider request failed.'},
                status=status.HTTP_502_BAD_GATEWAY
            )


class AIUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AIExecutionLog.objects.filter(user=request.user)

        totals = logs.aggregate(
            total_requests=Count('id'),
            improve_requests=Count(
                'id',
                filter=Q(action_type='improve')
            ),
            generate_requests=Count(
                'id',
                filter=Q(action_type='generate')
            ),
            total_tokens=Sum('tokens_used'),
            failed_requests=Count(
                'id',
                filter=Q(output_text__isnull=True)
            ),
        )

        providers = logs.values('provider').annotate(
            requests=Count('id'),
            tokens=Sum('tokens_used'),
            failed_requests=Count(
                'id',
                filter=Q(output_text__isnull=True)
            ),
        ).order_by('provider')

        return Response({
            'total_requests': totals['total_requests'],
            'improve_requests': totals['improve_requests'],
            'generate_requests': totals['generate_requests'],
            'total_tokens': totals['total_tokens'] or 0,
            'failed_requests': totals['failed_requests'],

            'by_provider': [
                {
                    'provider': item['provider'],
                    'requests': item['requests'],
                    'tokens': item['tokens'] or 0,
                    'failed_requests': item['failed_requests'],
                }
                for item in providers
            ],
        })