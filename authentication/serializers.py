
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.response import Response
from rest_framework import status


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password])
    password2 = serializers.CharField(write_only=True, )

    class Meta:
        model = User
        fields = ('password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {
                    "password": "Password fields didn't match."
                }
                )
        return attrs

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.save()
        UserSerializer(user)
        return user
