from rest_framework import status
from .serializers import (
    RegisterSerializer, UserSerializer,
    ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.encoding import (
    smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError)
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import serializers
from django.http import HttpResponsePermanentRedirect
import os


class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


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
                response_data = {"token": token, "user": serializer.data}
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


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64,
                                                  'token': token})

            redirect_url = request.data.get('redirect_url', '')
            print(redirect_url)
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use token below to reset your password  \
             \n token = '+token+'\n uid = '+uidb64
            try:
                send_mail("Password Reset Request", email_body,
                          "muhammad.aneeq@emumba.com",
                          [user.email], fail_silently=False)
            except BadHeaderError:
                return BaseApiView.failed("",
                                          "Invalid header",
                                          status.HTTP_400_BAD_REQUEST,
                                          "Invalid header")
            return BaseApiView.sucess("",
                                      "We have sent you a token to " +
                                      "reset your password ",
                                      status.HTTP_200_OK, None)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return BaseApiView.failed("",
                                          "Token is not valid," +
                                          " please request a new one",
                                          status.HTTP_400_BAD_REQUEST,
                                          "Token not valid")
            else:
                data = {"uidb64": uidb64, "token": token}
                return BaseApiView.sucess(data,
                                          "Credentials Valid",
                                          status.HTTP_200_OK, None)
        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
            except UnboundLocalError as e:
                return BaseApiView.failed("",
                                          "Token is not valid," +
                                          " please request a new one",
                                          status.HTTP_400_BAD_REQUEST,
                                          "Token not valid")


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        try:
            print(request.data)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            return BaseApiView.sucess("",
                                      "Password reset successfully",
                                      status.HTTP_200_OK, None)
        except Exception as identifier:
            print(identifier)
            return BaseApiView.failed("",
                                      "Token is invalid",
                                      status.HTTP_400_BAD_REQUEST,
                                      "Token not valid")


class refreshLogin(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            return BaseApiView.sucess(serializer.validated_data,
                                      "Access token generated successfully.",
                                      status.HTTP_201_CREATED, None)
            print(serializer.is_valid(raise_exception=True))
        else:
            return BaseApiView.sucess("",
                                      "Error Occured.",
                                      status.HTTP_201_CREATED,
                                      serializer.errors)

