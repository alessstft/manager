from django.contrib import admin
from django.urls import path
from new import views
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index', views.index),
    path('projects', views.projects),
    path('tasks', views.tasks),
    path('registr', views.registr),
    path('analit', views.analit),    
    path('team', views.team),
    path('vxod', views.vxod),
]