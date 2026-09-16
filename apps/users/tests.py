from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationTests(APITestCase):
	def test_register_login_and_logout(self):
		register_response = self.client.post(
			'/api/v1/auth/register/',
			{
				'email': 'new@example.com',
				'username': 'newuser',
				'password': 'StrongPassword123!',
			},
			format='json',
		)

		self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Token.objects.filter(user__email='new@example.com').exists())

		login_response = self.client.post(
			'/api/v1/auth/login/',
			{'email': 'new@example.com', 'password': 'StrongPassword123!'},
			format='json',
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Token {login_response.data['token']}")
		logout_response = self.client.post('/api/v1/auth/logout/')

		self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Token.objects.filter(user__email='new@example.com').exists())

	def test_registration_requires_username(self):
		response = self.client.post(
			'/api/v1/auth/register/',
			{'email': 'missing@example.com', 'password': 'StrongPassword123!'},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
