from django.urls import include, path

from authentication.views import (Login, PasswordTokenCheckAPI, RegisterView,
                                  RequestPasswordResetEmail,
                                  SetNewPasswordAPIView, refreshLogin)

urlpatterns = [
    path('auth/login/', Login.as_view(), name='auth_login'),
    path('auth/password-reset-email/', RequestPasswordResetEmail.as_view(),
         name='password-reset-email'),
    path('auth/token/refresh/', refreshLogin.as_view(), name='token_refresh'),
    path('users/', RegisterView.as_view(), name='auth_register'),
    path('auth/password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('auth/password-reset-confirm/', SetNewPasswordAPIView.as_view(),
         name='password-reset-confirm')
]
