from django.urls import path
from new import views
 
urlpatterns = [
    path('', views.index),
    path('projects', views.projects),
    path('tasks', views.tasks),
]