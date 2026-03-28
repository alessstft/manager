from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name

    def task_count(self):
        return self.tasks.count()

    def done_count(self):
        return self.tasks.filter(status='done').count()

    def progress(self):
        total = self.task_count()
        if total == 0:
            return 0
        return int(self.done_count() / total * 100)


class Task(models.Model):
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
        return self.title

    def status_color(self):
        return {'todo': 'secondary', 'in_progress': 'info', 'review': 'warning', 'done': 'success'}.get(self.status, 'secondary')

    def priority_color(self):
        return {'low': 'success', 'medium': 'warning', 'high': 'danger'}.get(self.priority, 'secondary')


class RelatedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='related_tasks')
    related = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='related_to')

    class Meta:
        unique_together = ('task', 'related')
        verbose_name = 'Связанная задача'
        verbose_name_plural = 'Связанные задачи'


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author.username} → {self.task.title}'


def task_file_path(instance, filename):
    return f'task_files/{instance.task.id}/{filename}'


class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=task_file_path)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def size_display(self):
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
        ext = self.original_name.rsplit('.', 1)[-1].lower() if '.' in self.original_name else ''
        return {
            'pdf': 'fa-file-pdf', 'doc': 'fa-file-word', 'docx': 'fa-file-word',
            'xls': 'fa-file-excel', 'xlsx': 'fa-file-excel',
            'png': 'fa-file-image', 'jpg': 'fa-file-image', 'jpeg': 'fa-file-image',
            'zip': 'fa-file-archive', 'rar': 'fa-file-archive',
            'js': 'fa-file-code', 'py': 'fa-file-code', 'json': 'fa-file-code',
        }.get(ext, 'fa-file')


class HistoryEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=500)
    icon = models.CharField(max_length=50, default='edit')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']