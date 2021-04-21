
import os

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from . import facebook
from .models import SocialProvider
from .register import register_social_user


class SocialProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialProvider
        fields = '__all__'


class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)

        try:
            return register_social_user(
                provider='facebook',
                user_id=user_data['id'],
                email=user_data['email'],
                name=user_data['name']
            )
        except Exception as identifier:
            raise serializers.ValidationError(
               identifier
            )
