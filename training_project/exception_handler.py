
import json
import logging

from base_api_view import BaseApiView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response:
        logger.error(response.data)
        return BaseApiView.failed("",
                                  "Error Occured.",
                                  status.HTTP_401_UNAUTHORIZED,
                                  response.data)
    logger.error(exc)
    return BaseApiView.failed("",
                              "Error Occured.",
                              status.HTTP_500_INTERNAL_SERVER_ERROR,
                              str(exc))
