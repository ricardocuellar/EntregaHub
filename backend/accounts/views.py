from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token, rotate_token
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import user_data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(trim_whitespace=False, write_only=True)


@method_decorator(never_cache, name='dispatch')
class CsrfView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'csrfToken': get_token(request)})


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        user = None
        if serializer.is_valid():
            user = authenticate(request=request, **serializer.validated_data)
        if user is None:
            return Response({'detail': 'Credenciales incorrectas.'},
                            status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response({
            'csrfToken': get_token(request),
            'user': user_data(user),
        })


@method_decorator(never_cache, name='dispatch')
class MeView(APIView):
    def get(self, request):
        return Response({'user': user_data(request.user)})


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        rotate_token(request)
        return Response({'csrfToken': get_token(request)})
