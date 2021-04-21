
from base_api_view import BaseApiView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import FacebookSocialAuthSerializer


class FacebookSocialAuthView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):

        """
        POST with "auth_token"
        Send an access token as from facebook to get user information
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = ((serializer.validated_data)['auth_token'])
        return BaseApiView.sucess(data,
                                  "User Logged in successfully.",
                                  status.HTTP_201_CREATED, None)
