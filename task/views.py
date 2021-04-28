import csv
from datetime import date, datetime, timedelta

from base_api_view import BaseApiView
from authentication.models import User
from django.db.models import Count, F, Max, Subquery, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import FileForm
from .models import Task, TaskFile
from .serializers import (FileInputSerializer, FileSerializer,
                          TaskInputSerializer, TaskSerializer)


class TaskList(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskInputSerializer

    def post(self, request, uid, format=None):
        request.data['user'] = uid
        due_date = request.data['due_date']
        due_date = due_date.split('T')[0]
        due_date = datetime. strptime(due_date, '%Y-%m-%d')
        if(due_date.date() < date.today()):
            error = {"due_date": "Invalid due_date"}
            return BaseApiView.failed_400(**error)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            task = {"task": serializer.data}
            return BaseApiView.sucess_201("Task created successfully.",
                                          **task)
        return BaseApiView.failed_400(**serializer.errors)

    def get(self, request, uid, format=None):
        task_list = Task.objects.filter(user=uid)
        if len(task_list) > 0:
            serializer = TaskSerializer(task_list, many=True)
            Tasks = {"tasks": serializer.data}
            return BaseApiView.sucess_200("Tasks retrieved successfully.",
                                          **Tasks)
        else:
            error = {"error": "Tasks Not Found"}
            return BaseApiView.failed_404(**error)


class TaskController(generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = TaskInputSerializer

    def get_task(self, pk):
        return get_object_or_404(Task, pk=pk)

    def get(self, request, uid, tid, format=None):
        task = Task.objects.filter(user=uid, id=tid)
        if len(task) > 0:
            serializer = TaskSerializer(task, many=True)
            Tasks = {"tasks": serializer.data}
            return BaseApiView.sucess_200("Tasks retrieved successfully.",
                                          **Tasks)
        else:
            error = {"error": "Tasks Not Found"}
            return BaseApiView.failed_404(**error)

    def put(self, request, uid, tid, format=None):
        task = self.get_task(tid)
        if task:
            request.data['date_posted'] = task.date_posted
            request.data['user'] = uid
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                task = {"task": serializer.data}
                return BaseApiView.sucess_200("Task updated successfully.",
                                              **task)
            return BaseApiView.failed_400(**serializer.errors)
        else:
            error = {"error": "Tasks Not Found"}
            return BaseApiView.failed_404(**error)

    def delete(self, request, uid, tid, format=None):
        task = self.get_task(tid)
        if task:
            file = TaskFile.objects.filter(task=task.id)
            if(len(file) >= 0):
                file.delete()
            task.delete()
            return BaseApiView.sucess_204()
        else:
            error = {"error": "Tasks Not Found"}
            return BaseApiView.failed_404(**error)


class FileController(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FileInputSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_task_file(self, pk):
        return TaskFile.objects.filter(task=pk)

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
            return BaseApiView.sucess_201("File attached successfully.",
                                          **payload)
        else:
            return BaseApiView.failed_400(**form.errors)

    def get(self, request, uid, tid, format=None):
        task_file = self.get_task_file(tid)
        if(len(task_file) > 0):
            file_serializer = FileSerializer(task_file, many=True)
            files = {"Files": file_serializer.data}
            return BaseApiView.sucess_200("Files retrieved successfully.",
                                          **files)
        else:
            error = {"error": "Files Not Found"}
            return BaseApiView.failed_404(**error)


class SimilarTasks(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskSerializer

    def get(self, request, uid, format=None):
        similar_tasks = set()
        tasks = Task.objects.filter(user=uid)
        duplicates = Task.objects.values('title', 'description')\
                         .annotate(Count('id')) \
                         .order_by()\
                         .filter(id__count__gt=1, user=2)

        similar_tasks = Task.objects.filter(
                         title__in=[item['title'] for item in duplicates],
                         description__in=[item['description']
                                          for item in duplicates])
        serializer = TaskSerializer(similar_tasks, many=True)
        similar_task = {"similar_tasks": serializer.data}
        return BaseApiView.sucess_200("Similar tasks.",
                                      **similar_task)


class Report1(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
        result = {}
        result['number_of_tasks'] = Task.objects.filter(user=uid).count()
        result['completed_tasks'] = Task.objects.filter(
                                    user=uid,
                                    completion_status=True).count()
        result['remaining_tasks'] = result['number_of_tasks'] - result['completed_tasks']
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
        result = {}
        result['late_tasks_completed'] = Task.objects.filter(
            user=uid,
            completion_date__gt=F('due_date')).count()
        return BaseApiView.sucess_200("Report Generated",
                                      **result)


class Report4(APIView):
    @method_decorator(cache_page(60*15))
    def get(self, request, uid, format=None):
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
            tasks_opened[
                date_joined.strftime("%A")+", " +
                date_joined.strftime("%Y-%m-%d")] = tasks
            date_joined += delta
        result = {
             "tasks_opened": tasks_opened,
        }
        return BaseApiView.sucess(result,
                                  "Report Generated",
                                  status.HTTP_200_OK, None)
