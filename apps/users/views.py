from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		token = Token.objects.create(user=user)

		return Response(
			{'token': token.key, 'user': UserSerializer(user).data},
			status=status.HTTP_201_CREATED,
		)


class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')
		user = authenticate(request, email=email, password=password)

		if user is None:
			return Response(
				{'detail': 'Invalid email or password.'},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		token, _ = Token.objects.get_or_create(user=user)
		return Response({'token': token.key, 'user': UserSerializer(user).data})


class LogoutView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		Token.objects.filter(user=request.user).delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
