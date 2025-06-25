from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Project(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

# class Task(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
#     assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
#     due_date = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     PRIORITY_CHOICES = [
#         ('low', 'Low'),
#         ('medium', 'Medium'),
#         ('high', 'High'),
#     ]
#     priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
#     STATUS_CHOICES = [
#         ('todo', 'To Do'),
#         ('in_progress', 'In Progress'),
#         ('done', 'Done'),
#     ]
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
#     def __str__(self):
#         return self.title
    
#     class Meta:
#         ordering = ['-priority', 'due_date']

# class Comment(models.Model):
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"Comment by {self.author.username} on {self.task.title}"

# class TimeLog(models.Model):
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField(null=True, blank=True)
#     duration = models.DurationField(null=True, blank=True)
    
#     def save(self, *args, **kwargs):
#         if self.end_time and not self.duration:
#             self.duration = self.end_time - self.start_time
#         super().save(*args, **kwargs)
    
#     def __str__(self):
#         return f"Time log for {self.task.title} by {self.user.username}"
