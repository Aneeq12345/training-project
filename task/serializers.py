from rest_framework import serializers
from .models import Task, TaskFile


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFile
        fields = '__all__'


class FileInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskFile
        fields = ('name', 'document')


class TaskInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('title', 'description', 'due_date', 'completion_date',
                  'completion_status')
