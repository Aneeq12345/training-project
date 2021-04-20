from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    completion_status = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TaskFile(models.Model):
    name = models.CharField(max_length=50)
    document = models.FileField(upload_to='documents/')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    class Meta:
        db_table = "documents"

    def __str__(self):
        return self.name
