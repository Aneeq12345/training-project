from django.shortcuts import render
from .models import Task,TaskFile
from .serializers import TaskSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from .forms import FileForm
class TaskController(APIView):
    """
    Add, Retrieve, update or delete a snippet instance.
    """
    permission_classes = (IsAuthenticated,)
    def get_object(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise Http404
    def post(self, request,format=None):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response({"success":True,"message":"Sucessfully Created!","result":serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)        

    def get(self, request,format=None):
        if request.data["user_id"]:
            taskList = Task.objects.filter(user=request.data["user_id"])
            serializer = TaskSerializer(taskList, many=True)
            return Response(serializer.data,status=status.HTTP)
        else:    
            task = self.get_object(pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)

    def put(self, request, format=None):
        task = self.get_object(request.data["id"])
        serializer = TaskSerializer(task,data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response({"success":True,"message":"Sucessfully Updated!","result":serializer.data})
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        Task = self.get_object(request.data["task_id"])
        file=TaskFile.objects.filter(task=Task.id)
        if(len(file)>=0):
            file.delete()
        Task.delete()
        return Response({"success":True,"message":"Sucessfully Deleted!"},status=status.HTTP_204_NO_CONTENT)

class FileController(APIView):
    def post(self, request, format=None):
        form = FileForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            print(form.cleaned_data["task"].id)
            return Response({"success":True,"message":"Sucessfully Uploaded!","result":{"name":form.cleaned_data["name"],"document":form.cleaned_data["name"],"task":form.cleaned_data["task"].id}},status=status.HTTP_201_CREATED)
        else:
            return Response({"success":False,"message":form.errors}, status=status.HTTP_400_BAD_REQUEST)