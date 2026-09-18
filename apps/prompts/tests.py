from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Prompt, PromptHistory


User = get_user_model()


class PromptAPITests(APITestCase):
	def setUp(self):
		self.owner = User.objects.create_user(
			email='owner@example.com', username='owner', password='StrongPassword123!'
		)
		self.other_user = User.objects.create_user(
			email='other@example.com', username='other', password='StrongPassword123!'
		)
		self.category = Category.objects.create(name='Writing')
		self.client.force_authenticate(self.owner)

	def prompt_payload(self, **overrides):
		payload = {
			'category': self.category.id,
			'title': 'Product announcement',
			'description': 'A concise announcement',
			'content': 'Write an announcement for a new product.',
			'is_public': False,
		}
		payload.update(overrides)
		return payload

	def test_prompt_crud_and_version_history(self):
		create_response = self.client.post(
			'/api/v1/prompts/', self.prompt_payload(), format='json'
		)
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		prompt_id = create_response.data['id']

		update_response = self.client.patch(
			f'/api/v1/prompts/{prompt_id}/',
			{'content': 'Write a professional product announcement.'},
			format='json',
		)
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)
		self.assertEqual(update_response.data['current_version'], 2)

		history_response = self.client.get(f'/api/v1/prompts/{prompt_id}/history/')
		self.assertEqual(history_response.status_code, status.HTTP_200_OK)
		self.assertEqual([item['version_number'] for item in history_response.data], [2, 1])

		delete_response = self.client.delete(f'/api/v1/prompts/{prompt_id}/')
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Prompt.objects.filter(id=prompt_id).exists())
		self.assertFalse(PromptHistory.objects.filter(prompt_id=prompt_id).exists())

	def test_private_prompt_is_hidden_from_other_users(self):
		prompt = Prompt.objects.create(
			user=self.owner,
			category=self.category,
			title='Private prompt',
			content='Private content',
			is_public=False,
		)
		self.client.force_authenticate(self.other_user)

		response = self.client.get(f'/api/v1/prompts/{prompt.id}/')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_public_prompt_can_be_viewed_by_other_users(self):
		prompt = Prompt.objects.create(
			user=self.owner,
			category=self.category,
			title='Public prompt',
			content='Public content',
			is_public=True,
		)
		self.client.force_authenticate(self.other_user)

		response = self.client.get(f'/api/v1/prompts/{prompt.id}/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_search_and_filters_are_applied(self):
		Prompt.objects.create(
			user=self.owner,
			category=self.category,
			title='Marketing prompt',
			content='Create marketing copy',
			is_public=True,
		)
		Prompt.objects.create(
			user=self.owner,
			category=self.category,
			title='Technical prompt',
			content='Explain an API',
			is_public=False,
		)

		response = self.client.get(
			'/api/v1/prompts/?search=marketing&is_public=true'
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['title'], 'Marketing prompt')

	def test_prompt_validation_rejects_missing_content(self):
		response = self.client.post(
			'/api/v1/prompts/',
			self.prompt_payload(content=''),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
