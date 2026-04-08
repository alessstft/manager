"""! @file models.py
@brief Domain models for projects, tasks and task history.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    """! @brief Project entity that groups tasks and team members."""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        """! @brief Returns readable project name."""
        return self.name

    def task_count(self):
        """! @brief Counts all tasks in the project."""
        return self.tasks.count()

    def done_count(self):
        """! @brief Counts tasks marked as done."""
        return self.tasks.filter(status='done').count()

    def progress(self):
        """! @brief Calculates completion percentage for the project."""
        total = self.task_count()
        if total == 0:
            return 0
        return int(self.done_count() / total * 100)


class Task(models.Model):
    """! @brief Work item linked to a specific project."""
    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('review', 'На проверке'),
        ('done', 'Завершено'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.PositiveSmallIntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        """! @brief Returns task title."""
        return self.title

    def status_color(self):
        """! @brief Returns Bootstrap color by task status."""
        return {'todo': 'secondary', 'in_progress': 'info', 'review': 'warning', 'done': 'success'}.get(self.status, 'secondary')

    def priority_color(self):
        """! @brief Returns Bootstrap color by task priority."""
        return {'low': 'success', 'medium': 'warning', 'high': 'danger'}.get(self.priority, 'secondary')


class RelatedTask(models.Model):
    """! @brief M2M-like link between two related tasks."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='related_tasks')
    related = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='related_to')

    class Meta:
        unique_together = ('task', 'related')
        verbose_name = 'Связанная задача'
        verbose_name_plural = 'Связанные задачи'


class Comment(models.Model):
    """! @brief User comment attached to a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """! @brief Returns compact comment identifier."""
        return f'{self.author.username} → {self.task.title}'


def task_file_path(instance, filename):
    """! @brief Builds upload path for a task attachment."""
    return f'task_files/{instance.task.id}/{filename}'


class TaskFile(models.Model):
    """! @brief File uploaded to a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=task_file_path)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def size_display(self):
        """! @brief Human-readable file size."""
        try:
            size = self.file.size
        except Exception:
            return '—'
        if size < 1024:
            return f'{size} Б'
        elif size < 1024 * 1024:
            return f'{size // 1024} КБ'
        return f'{size // (1024 * 1024)} МБ'

    def icon_class(self):
        """! @brief Font Awesome icon class based on extension."""
        ext = self.original_name.rsplit('.', 1)[-1].lower() if '.' in self.original_name else ''
        return {
            'pdf': 'fa-file-pdf', 'doc': 'fa-file-word', 'docx': 'fa-file-word',
            'xls': 'fa-file-excel', 'xlsx': 'fa-file-excel',
            'png': 'fa-file-image', 'jpg': 'fa-file-image', 'jpeg': 'fa-file-image',
            'zip': 'fa-file-archive', 'rar': 'fa-file-archive',
            'js': 'fa-file-code', 'py': 'fa-file-code', 'json': 'fa-file-code',
        }.get(ext, 'fa-file')


class HistoryEntry(models.Model):
    """! @brief Timeline event for changes in a task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=500)
    icon = models.CharField(max_length=50, default='edit')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']