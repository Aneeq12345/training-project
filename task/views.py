from django.shortcuts import render
from .models import Task, TaskFile
from .serializers import TaskSerializer, FileSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from .forms import FileForm
from datetime import date
from base_api_view import BaseApiView
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser


class TaskController(generics.CreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer
    token_param_config_user_id = openapi.Parameter(
        'user_id', in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING)

    token_param_config_task_id = openapi.Parameter(
        'task_id', in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING)

    def get_task(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return None

    def post(self, request, format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return BaseApiView.sucess(serializer.data,
                                      "Task created successfully.",
                                      status.HTTP_201_CREATED, None)
        return BaseApiView.failed("",
                                  "Error Occured.",
                                  status.HTTP_400_BAD_REQUEST,
                                  serializer.errors)

    @swagger_auto_schema(manual_parameters=[token_param_config_user_id])
    def get(self, request, format=None):
        task_list = Task.objects.filter(user=request.GET['user_id'])
        if len(task_list) > 0:
            serializer = TaskSerializer(task_list, many=True)
            return BaseApiView.sucess(serializer.data,
                                      "Tasks retrieved successfully.",
                                      status.HTTP_200_OK, None)
        else:
            return BaseApiView.failed("",
                                      "Tasks Not Found.",
                                      status.HTTP_404_NOT_FOUND,
                                      "")

    @swagger_auto_schema(manual_parameters=[token_param_config_task_id])
    def put(self, request, format=None):
        task = self.get_task(request.GET['task_id'])
        if task:
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return BaseApiView.sucess(serializer.data,
                                          "Task updated successfully.",
                                          status.HTTP_200_OK, None)
            return BaseApiView.failed("",
                                      "Error Occured.",
                                      status.HTTP_400_BAD_REQUEST,
                                      serializer.errors)
        else:
            return BaseApiView.failed("",
                                      "Tasks Not Found.",
                                      status.HTTP_404_NOT_FOUND,
                                      "")

    @swagger_auto_schema(manual_parameters=[token_param_config_task_id])
    def delete(self, request, format=None):
        task = self.get_task(request.GET["task_id"])
        if task:
            file = TaskFile.objects.filter(task=task.id)
            if(len(file) >= 0):
                file.delete()
            task.delete()
            return BaseApiView.sucess("",
                                      "Task deleted successfully.",
                                      status.HTTP_204_NO_CONTENT, None)
        else:
            return BaseApiView.failed("",
                                      "Task Not Found.",
                                      status.HTTP_204_NO_CONTENT, None)


class FileController(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileSerializer
    parser_classes = (FormParser, MultiPartParser)
    token_param_config_task_id = openapi.Parameter(
        'task_id', in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING)

    def get_task(self, pk):
        try:
            return TaskFile.objects.filter(task=pk)
        except Task.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        print(request.POST)
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            payload = {
                        "name": form.cleaned_data["name"],
                        "document": form.cleaned_data["name"],
                        "task": form.cleaned_data["task"].id
                    }
            return BaseApiView.sucess(payload,
                                      "File attached successfully.",
                                      status.HTTP_201_CREATED, None)
        else:
            return BaseApiView.failed("",
                                      "Error Occured.",
                                      status.HTTP_400_BAD_REQUEST,
                                      form.errors)

    @swagger_auto_schema(manual_parameters=[token_param_config_task_id])
    def get(self, request, format=None):
        task_file = self.get_task(request.GET['task_id'])
        if(len(task_file) > 0):
            file_serializer = FileSerializer(task_file, many=True)
            return BaseApiView.sucess({"Files": file_serializer.data},
                                      "Files retrieved successfully.",
                                      status.HTTP_200_OK, None)
        else:
            return BaseApiView.failed("",
                                      "Files not found.",
                                      status.HTTP_400_BAD_REQUEST,
                                      None)


class SimilarTasks(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get(self, request, format=None):
        similar_tasks = set()
        tasks = Task.objects.all()
        [similar_tasks.add(similar_task) for similar_task in tasks
         if tasks.filter(title=similar_task.title,
                         description=similar_task.description,
                         user=similar_task.user).count() > 1]
        serializer = TaskSerializer(similar_tasks, many=True)
        return BaseApiView.sucess(serializer.data,
                                  "Similar tasks.",
                                  status.HTTP_200_OK, None)
