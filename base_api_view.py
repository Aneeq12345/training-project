from rest_framework.response import Response
from rest_framework import status


class BaseApiView:
    def sucess_201(description, **data):
        return Response({
            "success": True,
            "payload": data,
            "errors": {},
            "description": description
            },
            status=status.HTTP_201_CREATED)

    def sucess_200(description, **data):
        return Response({
            "success": True,
            "payload": data,
            "errors": {},
            "description": description
            },
            status=status.HTTP_200_OK)

    def sucess_204():
        return Response({
            "success": True,
            "payload": {},
            "errors": {},
            "description": "Successfully Deleted"
            },
            status=status.HTTP_204_NO_CONTENT)

    def failed_401(**errors):
        return Response({
            "success": False,
            "payload": {},
            "errors": errors,
            "description": "Error Occured",
            },
            status=status.HTTP_401_UNAUTHORIZED)

    def failed_400(**errors):
        return Response({
            "success": False,
            "payload": {},
            "errors": errors,
            "description": "Error Occured",
            },
            status=status.HTTP_400_BAD_REQUEST)

    def failed_404(**errors):
        return Response({
            "success": False,
            "payload": {},
            "errors": errors,
            "description": "Error Occured",
            },
            status=status.HTTP_404_NOT_FOUND)
