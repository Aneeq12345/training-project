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
import logging
logger = logging.getLogger(__name__)


class TaskList(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskInputSerializer

    def post(self, request, uid, format=None):
        logger.info(request)
        logger.debug("Details Given are:")
        logger.debug(request.data)
        request.data['user'] = uid
        due_date = request.data['due_date']
        due_date = due_date.split('T')[0]
        due_date = datetime. strptime(due_date, '%Y-%m-%d')
        if(due_date.date() < date.today()):
            logger.error({"due_date": "Invalid due_date"})
            return BaseApiView.failed("",
                                      "Error Occured.",
                                      status.HTTP_400_BAD_REQUEST,
                                      {"due_date": "Invalid due_date"})
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.debug("Task created successfully")
            logger.debug(serializer.data)
            return BaseApiView.sucess(serializer.data,
                                      "Task created successfully.",
                                      status.HTTP_201_CREATED, None)
        logger.error(serializer.errors)
        return BaseApiView.failed("",
                                  "Error Occured.",
                                  status.HTTP_400_BAD_REQUEST,
                                  serializer.errors)

    def get(self, request, uid, format=None):
        logger.info(request)
        task_list = Task.objects.filter(user=uid)
        if len(task_list) > 0:
            serializer = TaskSerializer(task_list, many=True)
            logger.debug("Tasks retrieved successfully.")
            logger.debug(serializer.data)
            return BaseApiView.sucess(serializer.data,
                                      "Tasks retrieved successfully.",
                                      status.HTTP_200_OK, None)
        else:
            logger.error("Tasks not found.")
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
        logger.debug(request)
        task = Task.objects.filter(user=uid, id=tid)
        if len(task) > 0:
            serializer = TaskSerializer(task, many=True)
            logger.debug("Tasks retrieved successfully.")
            logger.debug(serializer.data)
            return BaseApiView.sucess(serializer.data,
                                      "Tasks retrieved successfully.",
                                      status.HTTP_200_OK, None)
        else:
            logger.error("Tasks not found.")
            return BaseApiView.failed("",
                                      "Tasks Not Found.",
                                      status.HTTP_404_NOT_FOUND,
                                      "")

    def put(self, request, uid, tid, format=None):
        logger.info(request)
        logger.debug("Details Given are:")
        logger.debug(request.data)
        task = self.get_task(tid)
        request.data['date_posted'] = task.date_posted
        request.data['user'] = uid
        if task:
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.debug("Task updated successfully.")
                logger.debug(serializer.data)
                return BaseApiView.sucess(serializer.data,
                                          "Task updated successfully.",
                                          status.HTTP_200_OK, None)
            logger.error(serializer.errors)
            return BaseApiView.failed("",
                                      "Error Occured.",
                                      status.HTTP_400_BAD_REQUEST,
                                      serializer.errors)
        else:
            logger.error("Tasks not found.")
            return BaseApiView.failed("",
                                      "Tasks Not Found.",
                                      status.HTTP_404_NOT_FOUND,
                                      "")

    def delete(self, request, uid, tid, format=None):
        logger.info(request)
        task = self.get_task(tid)
        if task:
            file = TaskFile.objects.filter(task=task.id)
            if(len(file) >= 0):
                file.delete()
            task.delete()
            logger.debug("Task deleted successfully")
            return BaseApiView.sucess("",
                                      "Task deleted successfully.",
                                      status.HTTP_204_NO_CONTENT, None)
        else:
            logger.error("Task not found")
            return BaseApiView.failed("",
                                      "Task Not Found.",
                                      status.HTTP_404_NOT_FOUND, None)


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
        logger.info(request)
        logger.debug("Details Given are:")
        data = {'name': request.POST['name'], 'task': tid}
        logger.debug(data)
        form = FileForm(data, request.FILES)
        if form.is_valid():
            form.save()
            payload = {
                        "name": form.cleaned_data["name"],
                        "document": form.cleaned_data["name"],
                        "task": form.cleaned_data["task"].id
                    }
            logger.debug("File attached successfully.")
            logger.debug(payload)
            return BaseApiView.sucess(payload,
                                      "File attached successfully.",
                                      status.HTTP_201_CREATED, None)
        else:
            logger.error(form.errors)
            return BaseApiView.failed("",
                                      "Error Occured.",
                                      status.HTTP_400_BAD_REQUEST,
                                      form.errors)

    def get(self, request, uid, tid, format=None):
        logger.info(request)
        task_file = self.get_task(tid)
        if(len(task_file) > 0):
            file_serializer = FileSerializer(task_file, many=True)
            logger.debug("Files retrieved successfully.")
            logger.debug({"Files": file_serializer.data})
            return BaseApiView.sucess({"Files": file_serializer.data},
                                      "Files retrieved successfully.",
                                      status.HTTP_200_OK, None)
        else:
            logger.error("Files not found.")
            return BaseApiView.failed("",
                                      "Files not found.",
                                      status.HTTP_400_BAD_REQUEST,
                                      None)


class SimilarTasks(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get(self, request, uid, format=None):
        logger.info(request)
        similar_tasks = set()
        tasks = Task.objects.filter(user=uid)
        [similar_tasks.add(similar_task) for similar_task in tasks
         if tasks.filter(title=similar_task.title,
                         description=similar_task.description,
                         user=similar_task.user).count() > 1]
        serializer = TaskSerializer(similar_tasks, many=True)
        logger.debug(serializer.data)
        return BaseApiView.sucess(serializer.data,
                                  "Similar tasks.",
                                  status.HTTP_200_OK, None)


class Report1(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        logger.info(request)
        result = {}
        result['number_of_tasks'] = Task.objects.filter(user=uid).count()
        result['completed_tasks'] = Task.objects.filter(
                                    user=uid,
                                    completion_status=True).count()
        result['remaining_tasks'] = Task.objects.filter(
                                    user=uid,
                                    completion_status=False).count()
        logger.debug(result)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report1.csv'
        # Create the CSV writer using the HttpResponse as the "file"
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['number_of_tasks', 'completed_tasks',
                        'remaining_tasks'])
        writer.writerow([result['number_of_tasks'], result['completed_tasks'],
                         result['remaining_tasks']])
        return response


class Report2(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        logger.info(request)
        user_joining_date = User.objects.values('date_joined').filter(id=uid)
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
        logger.debug(result)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report2.csv'
        # Create the CSV writer using the HttpResponse as the "file"
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(['avg_number_of_tasks_completed'])
        writer.writerow([count/days])
        return response


class Report3(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        logger.info(request)
        result = {}
        result['late_tasks_completed'] = Task.objects.filter(
            user=uid,
            completion_date__gt=F('due_date')).count()
        logger.debug(result)
        return BaseApiView.sucess(result,
                                  "Report Generated",
                                  status.HTTP_200_OK, None)


class Report4(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        logger.info(request)
        max_tasks_completed = Task.objects.values('completion_date')\
                                  .annotate(task_completed=Count('id'))\
                                  .filter(user=uid, completion_status=True)\
                                  .aggregate(Max('task_completed'))
        max_tasks_completed_on_date = Task.objects.values('completion_date')\
                                          .annotate(
                                              task_completed=Count('id'))\
                                          .filter(
                                              user=uid,
                                              completion_status=True)\
                                          .filter(
            task_completed=max_tasks_completed['task_completed__max'])
        if(max_tasks_completed['task_completed__max'] is not None):
            result = {
                        "max_tasks_completed": max_tasks_completed_on_date
                    }
            logger.debug(result)
            return BaseApiView.sucess(result,
                                      "Report Generated",
                                      status.HTTP_200_OK, None)
        else:
            logger.error("No result")
            return BaseApiView.failed("",
                                      "Tasks Not completed",
                                      status.HTTP_400_BAD_REQUEST, None)


class Report5(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        logger.info(request)
        user_joining_date = User.objects.values('date_joined').filter(id=uid)
        today = date.today()
        date_joined = user_joining_date[0]['date_joined'].date()
        delta = timedelta(days=1)
        tasks_opened = {}
        while date_joined <= today:
            tasks = Task.objects.filter(date_posted__date=date_joined,
                                        user=uid)\
                        .count()
            tasks_opened[
                date_joined.strftime("%A")+", " +
                date_joined.strftime("%Y-%m-%d")] = tasks
            date_joined += delta
        result = {
             "tasks_opened": tasks_opened,
        }
        logger.debug(result)
        return BaseApiView.sucess(result,
                                  "Report Generated",
                                  status.HTTP_200_OK, None)
