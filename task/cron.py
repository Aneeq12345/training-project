from .models import Task

from django.contrib.auth.models import User
from django.core.mail import send_mail
from datetime import date


def my_scheduled_job():
    today = date.today()
    task = Task.objects.filter(due_date=today).select_related('user')
    for tasks in task:
        send_mail(
            'Deadline',
            ''+tasks.title+' is due today',
            'muhammad.aneeq@emumba.com',
            [tasks.user.email], fail_silently=False)
