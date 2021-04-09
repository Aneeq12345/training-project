from django.shortcuts import render

# Create your views here.
from rest_framework import status
from .serializers import RegisterSerializer,UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import re
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from social_django.utils import psa
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
        

class Login(APIView):
    def validateEmail(self, email ):
        
        try:
            validate_email( email )
            return True
        except ValidationError:
            return False
    def getUser(self,email):
         try:
            return User.objects.get(email=email)
         except User.DoesNotExist:
            return "NOT FOUND"
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }        
    def get(self, request, format=None):

        email=request.data['email']
        if self.validateEmail(email):
            user = self.getUser(email=request.data['email'])
            if user=="NOT FOUND":
               return Response({"success":False,"message":"User Not Found!"},status=status.HTTP_404_NOT_FOUND)
            if user.check_password(request.data['password']):
                serializer=UserSerializer(user)
                token=self.get_tokens_for_user(user)
                return Response({"success":True,"message":"Sucessfully Login!","result":serializer.data,"token":token})
            return Response({"success":False,"message":"INVALID PASSWORD!"},status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response({"success":False,"message":"INVALID EMAIL ADDRESS!"},status=status.HTTP_400_BAD_REQUEST)    

from rest_framework import serializers  
class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """
    access_token = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

        
@api_view(http_method_names=['POST'])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):
    serializer = SocialSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        # This is the key line of code: with the @psa() decorator above,
        # it engages the PSA machinery to perform whatever social authentication
        # steps are configured in your SOCIAL_AUTH_PIPELINE. At the end, it either
        # hands you a populated User model of whatever type you've configured in
        # your project, or None.
        user = request.backend.do_auth(serializer.validated_data['access_token'])

        if user:
            # if using some other token back-end than DRF's built-in TokenAuthentication,
            # you'll need to customize this to get an appropriate token object
            print("hello")
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        else:
            return Response(
                {'errors': {'token': 'Invalid token'}},
                status=status.HTTP_400_BAD_REQUEST,
            )        