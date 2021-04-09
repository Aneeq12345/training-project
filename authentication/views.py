from django.shortcuts import render

# Create your views here.
from rest_framework import status
from .serializers import RegisterSerializer,UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from rest_framework import generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import re
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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

    
            
        
        