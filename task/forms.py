from django import forms

from .models import Task, TaskFile


class FileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = '__all__'
