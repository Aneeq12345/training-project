from rest_framework.response import Response


class BaseApiView:
    def sucess(data, description, status, errors, format=None):
        return Response({
            "success": True,
            "payload": data,
            "errors": errors,
            "description": description
            },
            status=status)

    def failed(data, description, status, errors, format=None):
        return Response({
            "success": False,
            "payload": data,
            "errors": errors,
            "description": description
            },
            status=status)
