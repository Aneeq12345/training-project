import logging
import os

from base_api_view import BaseApiView
from decouple import config
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import BadHeaderError, send_mail
from django.urls import reverse
from django.utils.encoding import (DjangoUnicodeDecodeError, force_bytes,
                                   force_str, smart_bytes, smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from validate_email import validate_email

from .models import User
from .serializers import (LoginSerializer, RegisterSerializer,
                          ResetPasswordEmailRequestSerializer,
                          SetNewPasswordSerializer, UserSerializer)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        try:
            if 'email' in request.data:
                request.data['email'] = request.data['email'].strip().lower()
            response = super().create(request, *args, **kwargs)
            return BaseApiView.sucess_201("User registered successfully.",
                                          **response.data)
        except Exception as identifier:
            error = {"error": identifier.args}
            logger.error(error)

            return BaseApiView.failed_400(**error)


class Login(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def get_user(self, email):
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
            user = self.get_user(email=email.strip().lower())
            if not user:
                error = {"error": "User not found"}
                return BaseApiView.failed_404(**error)
            if user.check_password(request.data['password']):
                serializer = UserSerializer(user)
                token = self.get_tokens_for_user(user)
                response_data = {"token": token, "user": serializer.data}
                return BaseApiView.sucess_200("User logged in successfully.",
                                              **response_data)
            error = {"error": "Credentials not valid"}
            return BaseApiView.failed_400(**error)
        else:
            error = {"error": "Credentials not valid"}
            return BaseApiView.failed_400(**error)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            email_body = 'Hello, \n Use token below to reset your password  \
             \n token = '+token+'\n uid = '+uidb64
            try:
                send_mail("Password Reset Request", email_body,
                          config('EMAIL_FROM'),
                          [user.email], fail_silently=False)
            except BadHeaderError:
                error = {"error": "Invalid header"}
                return BaseApiView.failed_400(**error)
            return BaseApiView.sucess_200("We have sent you a token to " +
                                          "reset your password ",
                                          **{})


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                error = {
                    "error": "Token is not valid,please request a new one"
                    }
                return BaseApiView.failed_400(**error)
            else:
                data = {"uidb64": uidb64, "token": token}
                return BaseApiView.sucess_200("Credentials Valid",
                                              **data)
        except DjangoUnicodeDecodeError as identifier:
            logger.error(identifier)
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    error = {
                        "error": "Token is not valid,please request a new one"
                    }
                    return BaseApiView.failed_400(**error)
            except UnboundLocalError as e:
                logger.error(e)
                return BaseApiView.failed_400(**e)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = (AllowAny,)

    def patch(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            return BaseApiView.sucess_200("Password reset successfully.",
                                          **{})
        except Exception as identifier:
            logger.error(identifier)
            error = {"error": str(identifier)}
            return BaseApiView.failed_400(**error)


class refreshLogin(TokenRefreshView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return BaseApiView.sucess_200("Access token generated successfully.",
                                          **serializer.validated_data)
        else:
            return BaseApiView.failed_400(**serializer.errors)
