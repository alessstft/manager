from django.contrib import admin
from .models import Project, Task, TaskFile, Comment, HistoryEntry

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'executor', 'deadline', 'progress')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description')
    filter_horizontal = ('related_tasks',)


@admin.register(TaskFile)
class TaskFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'task', 'uploaded_at', 'uploaded_by')
    list_filter = ('task',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('task',)


@admin.register(HistoryEntry)
class HistoryEntryAdmin(admin.ModelAdmin):
    list_display = ('task', 'action', 'user', 'timestamp')
    list_filter = ('task',)
