
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
        if response.data['detail'] == 'Authentication credentials were not provided':
            return BaseApiView.failed_401(**response.data)
        return BaseApiView.failed_400(**response.data)
    error = {"error": str(exc)}
    logger.error(error)
    return BaseApiView.failed_400(**error)
