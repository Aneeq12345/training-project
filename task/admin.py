from django.contrib import admin

# Register your models here.
from .models import Task, TaskFile

admin.site.register(Task)
admin.site.register(TaskFile)
