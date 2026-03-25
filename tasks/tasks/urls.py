from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from new import views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile_view, name='profile'),
    path(
        'employees/new/',
        user_views.admin_create_employee,
        name='admin_create_employee',
    ),
    path('login/', user_views.login_view, name='login'),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            template_name='users/logout.html',
        ),
        name='logout',
    ),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html'
        ),
        name='password_reset',
    ),
    path('', views.index, name='home'),
    path('index/', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('tasks/', views.tasks, name='tasks'),
    path('team/', views.team, name='team'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
