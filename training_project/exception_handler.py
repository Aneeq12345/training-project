
from rest_framework.response import Response
from base_api_view import BaseApiView
from rest_framework import status
from rest_framework.views import exception_handler
import json
from json import dumps, loads, JSONEncoder, JSONDecoder
# from django.utils.six.moves.http_client import responses


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response:
        return BaseApiView.failed("",
                                  "Error Occured.",
                                  status.HTTP_401_UNAUTHORIZED,
                                  response.data)
    return BaseApiView.failed("",
                              "Error Occured.",
                              status.HTTP_500_INTERNAL_SERVER_ERROR,
                              str(exc))
