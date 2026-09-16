from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AIExecutionLog
from .providers.anthropic_provider import AnthropicProvider
from .providers.factory import AIProviderFactory
from .providers.openai_providers import OpenAIProvider


User = get_user_model()


class AIServiceTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email='ai-user@example.com', username='aiuser', password='StrongPassword123!'
		)
		self.client.force_authenticate(self.user)

	@patch('apps.ai_service.views.AIProviderFactory.get_provider')
	def test_improve_success_is_logged(self, get_provider):
		provider = Mock()
		provider.improve_prompt.return_value = (
			'Improved prompt',
			{'model': 'test-model', 'prompt_tokens': 10, 'completion_tokens': 5},
		)
		get_provider.return_value = provider

		response = self.client.post(
			'/api/v1/ai/improve/',
			{'prompt_content': 'Improve this', 'provider': 'openai'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		log = AIExecutionLog.objects.get(user=self.user)
		self.assertEqual(log.provider, 'openai')
		self.assertEqual(log.action_type, 'improve')
		self.assertEqual(log.output_text, 'Improved prompt')
		self.assertEqual(log.tokens_used, 15)

	@patch('apps.ai_service.views.AIProviderFactory.get_provider')
	def test_provider_failure_returns_bad_gateway_and_is_logged(self, get_provider):
		provider = Mock()
		provider.generate_prompt.side_effect = RuntimeError('upstream unavailable')
		get_provider.return_value = provider

		response = self.client.post(
			'/api/v1/ai/generate/',
			{'description': 'Generate a prompt', 'provider': 'anthropic'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
		log = AIExecutionLog.objects.get(user=self.user)
		self.assertEqual(log.provider, 'anthropic')
		self.assertIsNone(log.output_text)

	def test_unsupported_provider_returns_bad_request_and_is_logged(self):
		response = self.client.post(
			'/api/v1/ai/improve/',
			{'prompt_content': 'Improve this', 'provider': 'unsupported'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertTrue(
			AIExecutionLog.objects.filter(
				user=self.user, provider='unsupported', action_type='improve'
			).exists()
		)

	def test_usage_endpoint_returns_user_statistics(self):
		AIExecutionLog.objects.create(
			user=self.user,
			provider='openai',
			action_type='improve',
			input_text='one',
			output_text='result',
			tokens_used=12,
		)
		AIExecutionLog.objects.create(
			user=self.user,
			provider='anthropic',
			action_type='generate',
			input_text='two',
			tokens_used=0,
		)

		response = self.client.get('/api/v1/ai/usage/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['total_requests'], 2)
		self.assertEqual(response.data['improve_requests'], 1)
		self.assertEqual(response.data['generate_requests'], 1)
		self.assertEqual(response.data['total_tokens'], 12)
		self.assertEqual(response.data['failed_requests'], 1)
		self.assertEqual(len(response.data['by_provider']), 2)

	def test_factory_supports_both_providers(self):
		self.assertIn('openai', AIProviderFactory._providers)
		self.assertIn('anthropic', AIProviderFactory._providers)

	@patch('apps.ai_service.providers.openai_providers.OpenAI')
	def test_openai_provider_normalizes_response(self, openai_client):
		response = Mock()
		response.choices = [Mock(message=Mock(content='OpenAI result'))]
		response.usage.prompt_tokens = 7
		response.usage.completion_tokens = 3
		openai_client.return_value.chat.completions.create.return_value = response

		result, metadata = OpenAIProvider().generate_prompt('Generate a prompt')

		self.assertEqual(result, 'OpenAI result')
		self.assertEqual(metadata['prompt_tokens'], 7)
		self.assertEqual(metadata['completion_tokens'], 3)

	@patch('apps.ai_service.providers.anthropic_provider.Anthropic')
	def test_anthropic_provider_normalizes_response(self, anthropic_client):
		response = Mock()
		response.content = [Mock(text='Anthropic result')]
		response.usage.input_tokens = 8
		response.usage.output_tokens = 4
		anthropic_client.return_value.messages.create.return_value = response

		result, metadata = AnthropicProvider().generate_prompt('Generate a prompt')

		self.assertEqual(result, 'Anthropic result')
		self.assertEqual(metadata['prompt_tokens'], 8)
		self.assertEqual(metadata['completion_tokens'], 4)
