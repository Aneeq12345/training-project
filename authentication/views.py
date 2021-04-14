from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from validate_email import validate_email
from .response import BaseApiView


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return BaseApiView.sucess(response.data,
                                  "User registered successfully.",
                                  status.HTTP_201_CREATED, None)


class Login(APIView):
    def getUser(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)}

    def post(self, request, format=None):
        email = request.data['email']
        if validate_email(email):
            user = self.getUser(email=email)
            if not user:
                return BaseApiView.failed("",
                                          "User Not Found!",
                                          status.HTTP_404_NOT_FOUND, None)
            if user.check_password(request.data['password']):
                serializer = UserSerializer(user)
                token = self.get_tokens_for_user(user)
                response_data = [token, serializer.data]
                return BaseApiView.sucess(response_data,
                                          "User logged in successfully.",
                                          status.HTTP_200_OK, None)
            return BaseApiView.failed("",
                                      "INVALID PASSWORD!",
                                      status.HTTP_400_BAD_REQUEST, None)
        else:
            return BaseApiView.failed("",
                                      "INVALID EMAIL ADDRESS!",
                                      status.HTTP_400_BAD_REQUEST, None)
