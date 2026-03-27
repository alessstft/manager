from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from new import views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', user_views.register, name='register'),
    path('profile', user_views.profile, name='profile'),
    path('login',
         auth_views.LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='users/logout.html'),
         name='logout'),
    path('password-reset',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),

    # main pages
    path('', views.index, name='home'),
    path('index', views.index, name='index'),
    path('projects', views.projects, name='projects'),
    path('tasks', views.tasks, name='tasks'),
    path('team', views.team, name='team'),

    # project CRUD
    path('projects/create', views.create_project, name='create_project'),
    path('projects/<int:pk>/edit', views.edit_project, name='edit_project'),
    path('projects/<int:pk>/delete', views.delete_project, name='delete_project'),

    # task CRUD
    path('tasks/create', views.create_task, name='create_task'),
    path('tasks/<int:pk>/edit', views.edit_task, name='edit_task'),
    path('tasks/<int:pk>/delete', views.delete_task, name='delete_task'),

    # comments & files
    path('tasks/<int:task_pk>/comment', views.add_comment, name='add_comment'),
    path('tasks/<int:task_pk>/upload', views.upload_file, name='upload_file'),
    path('files/<int:file_pk>/delete', views.delete_file, name='delete_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
