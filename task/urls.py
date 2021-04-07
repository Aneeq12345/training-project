from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    
    path('', views.TaskController.as_view(),name='TaskController'),
    path('files/', views.FileController.as_view(),name='FileController'),
]
