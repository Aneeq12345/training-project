from django.urls import path, include
from authentication.views import RegisterView, Login
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', Login.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
]
