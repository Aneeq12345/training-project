from django.shortcuts import render
from .models import Task, TaskFile
from .serializers import (TaskSerializer, FileSerializer,
                          TaskInputSerializer, FileInputSerializer)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from .forms import FileForm
from datetime import date, datetime, timedelta
from base_api_view import BaseApiView
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import FormParser, MultiPartParser
import jwt
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, F, Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, JsonResponse
import csv


class TaskList(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskInputSerializer

    def post(self, request, uid, format=None):
        request.data['user'] = uid
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

    def get(self, request, uid, format=None):
        task_list = Task.objects.filter(user=uid)
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


class TaskController(generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = TaskInputSerializer

    def get_task(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return None

    def get(self, request, uid, tid, format=None):
        task = Task.objects.filter(user=uid, id=tid)
        if len(task) > 0:
            serializer = TaskSerializer(task, many=True)
            return BaseApiView.sucess(serializer.data,
                                      "Tasks retrieved successfully.",
                                      status.HTTP_200_OK, None)
        else:
            return BaseApiView.failed("",
                                      "Tasks Not Found.",
                                      status.HTTP_404_NOT_FOUND,
                                      "")

    def put(self, request, uid, tid, format=None):
        task = self.get_task(tid)
        request.data['date_posted'] = task.date_posted
        request.data['user'] = uid
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

    def delete(self, request, uid, tid, format=None):
        task = self.get_task(tid)
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
    serializer_class = FileInputSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_task(self, pk):
        try:
            return TaskFile.objects.filter(task=pk)
        except Task.DoesNotExist:
            raise Http404

    def post(self, request, uid, tid, format=None):
        data = {'name': request.POST['name'], 'task': tid}
        form = FileForm(data, request.FILES)
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

    def get(self, request, uid, tid, format=None):
        task_file = self.get_task(tid)
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

    def get(self, request, uid, format=None):
        similar_tasks = set()
        tasks = Task.objects.filter(user=uid)
        [similar_tasks.add(similar_task) for similar_task in tasks
         if tasks.filter(title=similar_task.title,
                         description=similar_task.description,
                         user=similar_task.user).count() > 1]
        serializer = TaskSerializer(similar_tasks, many=True)
        return BaseApiView.sucess(serializer.data,
                                  "Similar tasks.",
                                  status.HTTP_200_OK, None)


class Report1(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        task_count = Task.objects.filter(user=uid).count()
        completed_task = Task.objects.filter(user=uid,
                                             completion_status=True).count()
        remaining_task = Task.objects.filter(user=uid,
                                             completion_status=False).count()
        result = {
                    "number_of_tasks": task_count,
                    "completed_tasks": completed_task,
                    "remaining_tasks": remaining_task
                }
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report1.csv'
        # Create the CSV writer using the HttpResponse as the "file"
        writer = csv.writer(response)
        writer.writerow(['number_of_tasks', 'completed_tasks','remaining_tasks'])
        writer.writerow([task_count, completed_task, remaining_task])
        return response


class Report2(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        user_joining_date = User.objects.values('date_joined').filter(id=uid)
        print(user_joining_date)
        today = date.today()
        date_joined = user_joining_date[0]['date_joined'].date()
        delta = timedelta(days=1)
        tasks_opened = {}
        days = 0
        count = 0
        while date_joined <= today:
            tasks = Task.objects.filter(completion_date__date=date_joined,
                                        user=uid)\
                        .count()
            days += 1
            date_joined += delta
            count += tasks
        result = {
             "avg_number_of_tasks_completed": count/days,
        }
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report2.csv'
        # Create the CSV writer using the HttpResponse as the "file"
        writer = csv.writer(response)
        writer.writerow(['avg_number_of_tasks_completed'])
        writer.writerow([count/days])
        return response


class Report3(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        late_tasks_completed = Task.objects.filter(user=uid,
                                                   completion_date__gt=F('due_date')).count()
        result = {
                    "late_tasks_completed": late_tasks_completed
                }
        return BaseApiView.sucess(result,
                                  "Report Generated",
                                  status.HTTP_200_OK, None)   


class Report4(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        max_tasks_completed = Task.objects.values('completion_date')\
                                  .annotate(task_completed=Count('id'))\
                                  .filter(user=uid, completion_status=True)\
                                  .aggregate(Max('task_completed'))
        print(max_tasks_completed)
        max_tasks_completed_on_date = Task.objects.values('completion_date')\
                                          .annotate(
                                              task_completed=Count('id'))\
                                          .filter(
                                              user=uid,
                                              completion_status=True)\
                                          .filter(
                                              task_completed=max_tasks_completed['task_completed__max'])
        if(max_tasks_completed['task_completed__max']!=None):
            result = {
                        "max_tasks_completed": max_tasks_completed_on_date 
                    }
            return BaseApiView.sucess(result,
                                      "Report Generated",
                                      status.HTTP_200_OK, None)
        else:
            return BaseApiView.failed("",
                                      "Tasks Not completed",
                                      status.HTTP_400_BAD_REQUEST, None)


class Report5(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        user_joining_date = User.objects.values('date_joined').filter(id=uid)
        today = date.today()
        date_joined = user_joining_date[0]['date_joined'].date()
        delta = timedelta(days=1)
        tasks_opened = {}
        while date_joined <= today:
            tasks = Task.objects.filter(date_posted__date=date_joined,
                                        user=uid)\
                        .count()
            print(date_joined.strftime("%Y-%m-%d"))
            print(date_joined.strftime("%A"))
            tasks_opened[date_joined.strftime("%A")+", "+date_joined.strftime("%Y-%m-%d")] = tasks
            print(tasks)
            date_joined += delta
        result = {
             "tasks_opened": tasks_opened,
        }
        return BaseApiView.sucess(result,
                                  "Report Generated",
                                  status.HTTP_200_OK, None)
