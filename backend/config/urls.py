from django.urls import path
from accounts.views import CsrfView, LoginView, LogoutView, MeView
from core.views import health
urlpatterns = [
    path('api/health/', health),
    path('api/auth/csrf/', CsrfView.as_view()),
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/me/', MeView.as_view()),
    path('api/auth/logout/', LogoutView.as_view()),
]
