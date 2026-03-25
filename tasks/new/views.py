from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from users.models import Profile

from .models import Post


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'new/home.html', context)

def index(request):
    return render(
        request,
        "index.html",
        {"admin_registered": Profile.has_admin()},
    )
 
@login_required
def projects(request):
    return render(request, 'projects.html')


@login_required
def tasks(request):
    return render(request, 'tasks.html')


@login_required
def team(request):
    return render(request, 'team.html')

def registr(request):
    return render(request, 'registr.html')
