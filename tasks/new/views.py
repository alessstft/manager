from django.shortcuts import render
 
def index(request):
    return render(request, "index.html")
 
def projects(request):
    return render(request, 'projects.html')

def tasks(request):
    return render(request, 'tasks.html')