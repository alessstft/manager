from django.shortcuts import render
from .models import Post
 
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

def vxod(request):
    return render(request, 'vxod.html')

def analit(request):
    return render(request, 'analit.html')