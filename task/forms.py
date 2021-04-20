from django import forms
from .models import TaskFile, Task


class FileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = '__all__'
