from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [

    path('<int:uid>/tasks/<int:tid>', views.TaskController.as_view(),
         name='TaskController'),
    path('<int:uid>/tasks/', views.TaskList.as_view(),
         name='Task-Controller'),
    # path('', views.TaskController.as_view(), name='TaskController'),
    path('<int:uid>/tasks/similars/', views.SimilarTasks.as_view(),
         name='similar'),
    path('<int:uid>/tasks/<int:tid>/files/', views.FileController.as_view(),
         name='FileController'),
    path('<int:uid>/report1/', views.Report1.as_view(), name='report1'),
    path('<int:uid>/report2/', views.Report2.as_view(), name='report2'),
    path('<int:uid>/report3/', views.Report3.as_view(), name='report3'),
    path('<int:uid>/report4/', views.Report4.as_view(), name='report4'),
    path('<int:uid>/report5/', views.Report5.as_view(), name='report5'),
]
