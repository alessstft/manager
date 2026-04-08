"""! @file views.py
@brief Authentication, employee onboarding and profile management views.
"""

from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import (
    AdminCreateEmployeeForm,
    FirstAdminRegistrationForm,
    ProfileUpdateForm,
    UserUpdateForm,
)
from .models import Profile


def company_admin_required(view_func):
    """! @brief Restricts endpoint access to authenticated admins only."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        try:
            if request.user.profile.role != Profile.Role.ADMIN:
                messages.error(request, 'Эта страница доступна только администратору.')
                return redirect('projects')
        except Profile.DoesNotExist:
            messages.error(request, 'Профиль не найден.')
            return redirect('profile')
        return view_func(request, *args, **kwargs)

    return _wrapped


@ensure_csrf_cookie
def login_view(request):
    """! @brief Authenticates user and redirects to projects page."""
    if request.user.is_authenticated:
        return redirect('projects')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('projects')
        messages.error(request, 'Неверный логин или пароль.')
    return render(
        request,
        'users/login.html',
        {'admin_registered': Profile.has_admin()},
    )


def register(request):
    """! @brief Registers the first administrator account."""
    if Profile.has_admin():
        return render(request, 'users/register_closed.html')
    if request.user.is_authenticated:
        return redirect('projects')
    if request.method == 'POST':
        form = FirstAdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            profile = user.profile
            profile.role = Profile.Role.ADMIN
            profile.save()
            messages.success(
                request,
                'Администратор создан. Войдите с выбранным логином и паролем.',
            )
            return redirect('login')
    else:
        form = FirstAdminRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
@company_admin_required
def admin_create_employee(request):
    """! @brief Admin-only endpoint for creating employee accounts."""
    if request.method == 'POST':
        form = AdminCreateEmployeeForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.role = Profile.Role.EMPLOYEE
            profile.save()
            messages.success(
                request,
                f'Сотрудник создан. Логин: «{user.username}». '
                'Передайте пароль сотруднику для входа.',
            )
            return redirect('admin_create_employee')
    else:
        form = AdminCreateEmployeeForm()
    return render(
        request,
        'users/create_employee.html',
        {'form': form, 'employees': User.objects.filter(profile__role=Profile.Role.EMPLOYEE)},
    )


@login_required
def profile_view(request):
    """! @brief Displays and updates current user profile."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile,
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        'users/profile.html',
        {
            'u_form': u_form,
            'p_form': p_form,
            'profile': profile,
        },
    )
