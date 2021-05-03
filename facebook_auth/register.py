import os
import random

from decouple import config
from authentication.models import User
from django.contrib.auth import authenticate, get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SocialProvider


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email, name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():
        auth_provider = SocialProvider.objects.filter(
            user=filtered_user_by_email[0].id)
        if len(auth_provider) != 0 and provider == auth_provider[0].provider:
            registered_user = authenticate(
                username=email, password=config('SOCIAL_SECRET'))
            response_payload = {
                                "user": {
                                    'id': registered_user.id,
                                    'email': registered_user.email,
                                    'first_name': registered_user.first_name,
                                    'last_name': registered_user.last_name

                                    },
                                "tokens": get_tokens_for_user(registered_user)

                            }
            return response_payload
        else:
            raise AuthenticationFailed("User already exists")

    else:
        user = {
            'username': email, 'email': email,
            'password': config('SOCIAL_SECRET')}

        user = User.objects.create_user(**user)
        user.is_verified = True
        new_user = authenticate(
            username=email, password=config('SOCIAL_SECRET'))
        provider = {
            'provider': "facebook",
            'user': user
        }
        SocialProvider.objects.create(**provider)
        response_payload = {
                "user": {
                    'id': new_user.id,
                    'email': new_user.email,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name

                    },
                "tokens": get_tokens_for_user(new_user)

            }
        return response_payload
