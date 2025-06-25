from django.shortcuts import render
from .models import Post

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'new/home.html', context)

def index(request):
    return render(request, "index.html")
 
def projects(request):
    return render(request, 'projects.html')

def tasks(request):
    return render(request, 'tasks.html')

def team(request):
    return render(request, 'team.html')

def registr(request):
    return render(request, 'registr.html')
