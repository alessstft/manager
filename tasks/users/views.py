from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import ProfileUpdateForm, UserRegisterForm, UserUpdateForm

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('projects')  # Убедитесь что этот URL существует
        else:
            messages.error(request, 'Неверный email или пароль')
    return render(request, 'users/login.html')

def register(request):
    if request.method == 'POST':
        if User.objects.filter(is_superuser=True).exists():
            form = UserRegisterForm(request.POST)
            messages.error(
                request,
                "Администратор уже создан. Через эту форму можно создать только первого администратора.",
            )
            return render(request, 'users/register.html', {'form': form})

        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request,
                f'Администратор {username} создан. Теперь можно войти в систему.',
            )
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Профиль обновлён")
            return redirect("profile")
        messages.error(request, "Проверьте ошибки в форме")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        "users/profile.html",
        {"u_form": u_form, "p_form": p_form},
    )

@login_required
def projects(request):
    return render(request, 'projects.html')