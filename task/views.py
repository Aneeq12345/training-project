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


class TaskController(APIView):

    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Sucessfully Created!",
                    "result": serializer.data
                },
                status=status.HTTP_201_CREATED)
        return Response(
            {
                "success": False,
                "message": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        task_list = Task.objects.filter(user=request.data["id"])
        serializer = TaskSerializer(task_list, many=True)
        return Response(
            {
                "success": True,
                "message": "Sucessfull Query!",
                "result": serializer.data
            })

    def put(self, request, format=None):
        task = self.get_object(request.data["id"])
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Sucessfully Updated!",
                    "result": serializer.data
                })
        return Response(
            {
                "success": False,
                "message": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        task = self.get_object(request.data["task_id"])
        file = TaskFile.objects.filter(task=task.id)
        if(len(file) >= 0):
            file.delete()
        task.delete()
        return Response(
            {
                "success": True,
                "message": "Sucessfully Deleted!"
            },
            status=status.HTTP_204_NO_CONTENT)


class FileController(APIView):
    def get_object(self, pk):
        try:
            return TaskFile.objects.filter(task=pk)
        except Task.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return Response(
                {
                    "success": True,
                    "message": "Sucessfully Uploaded!",
                    "result": {
                        "name": form.cleaned_data["name"],
                        "document": form.cleaned_data["name"],
                        "task": form.cleaned_data["task"].id
                    }
                },
                status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    "success": False,
                    "message": form.errors
                },
                status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        task_file = self.get_object(request.data["task_id"])
        if(len(task_file) > 0):
            file_serializer = FileSerializer(task_file, many=True)
            return Response(
                {
                    "success": True,
                    "message": "Sucessfull Query!",
                    "result": file_serializer.data
                })
        else:
            return Response(
                {
                    "success": False,
                    "message": "NOT FOUND!"
                },
                status=status.HTTP_404_NOT_FOUND)


class SimilarTasks(APIView):
    def get(self, request, format=None):
        similar_tasks = set()
        tasks = Task.objects.all()
        [similar_tasks.add(similar_task) for similar_task in tasks
         if tasks.filter(title=similar_task.title,
                         description=similar_task.description,
                         user=similar_task.user).count() > 1]
        serializer = TaskSerializer(similar_tasks, many=True)
        return Response(
            {
                "success": True,
                "message": "Sucessfull Query!",
                "result": serializer.data
            })
