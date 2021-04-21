
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .serializers import FacebookSocialAuthSerializer
from rest_framework.permissions import AllowAny
from base_api_view import BaseApiView
import logging
logger = logging.getLogger(__name__)


class FacebookSocialAuthView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):
        logger.info(request)
        logger.debug("Details Given are:")
        logger.debug(request.data)
        """
        POST with "auth_token"
        Send an access token as from facebook to get user information
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        data = ((serializer.validated_data)['auth_token'])
        logger.debug("User Logged in successfully.")
        logger.debug(data)
        return BaseApiView.sucess(data,
                                  "User Logged in successfully.",
                                  status.HTTP_201_CREATED, None)
