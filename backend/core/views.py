from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def csrf_failure(request, reason=''):
    return JsonResponse({'detail': 'Verificación CSRF rechazada. Recarga la página e inténtalo otra vez.'}, status=403)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    return Response({'status': 'ok', 'service': 'EntregaPRO API'})
