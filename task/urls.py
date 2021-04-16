from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [

    path('tasks/', views.TaskController.as_view(),
         name='TaskController'),
    # path('', views.TaskController.as_view(), name='TaskController'),
    path('tasks/similars/', views.SimilarTasks.as_view(), name='similar'),
    path('tasks/files/', views.FileController.as_view(),
         name='FileController'),
]
