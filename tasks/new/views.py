import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from users.models import Profile
from .models import Comment, HistoryEntry, Project, RelatedTask, Task, TaskFile


# ─── helpers ────────────────────────────────────────────────

def _is_admin(user):
    try:
        return user.profile.role == Profile.Role.ADMIN
    except Profile.DoesNotExist:
        return False

def _uname(user):
    return user.get_full_name().strip() or user.username

def _hist(task, user, action, icon='edit'):
    HistoryEntry.objects.create(task=task, user=user, action=action, icon=icon)


# ─── index ──────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html', {'admin_registered': Profile.has_admin()})


# ─── projects ───────────────────────────────────────────────

@login_required
def projects(request):
    if _is_admin(request.user):
        qs = Project.objects.all()
    else:
        qs = (Project.objects.filter(members=request.user) |
              Project.objects.filter(owner=request.user)).distinct()

    all_users = User.objects.select_related('profile').all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        start_date = request.POST.get('start_date') or None
        end_date   = request.POST.get('end_date')   or None
        member_ids = request.POST.getlist('members')
        if name:
            project = Project.objects.create(
                name=name, description=description, priority=priority,
                start_date=start_date, end_date=end_date, owner=request.user,
            )
            if member_ids:
                project.members.set(User.objects.filter(id__in=member_ids))
            project.members.add(request.user)
            messages.success(request, f'Проект «{project.name}» создан.')
            return redirect('projects')
        else:
            messages.error(request, 'Укажите название проекта.')

    return render(request, 'projects.html', {
        'projects': qs, 'all_users': all_users, 'is_admin': _is_admin(request.user)
    })


@login_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and not _is_admin(request.user):
        messages.error(request, 'Нет прав для удаления.')
        return redirect('projects')
    name = project.name
    project.delete()
    messages.success(request, f'Проект «{name}» удалён.')
    return redirect('projects')


# ─── tasks list ─────────────────────────────────────────────

@login_required
def tasks_list(request):
    if _is_admin(request.user):
        task_qs = Task.objects.select_related('project', 'assigned_to', 'created_by').all()
    else:
        task_qs = Task.objects.filter(
            project__members=request.user
        ).select_related('project', 'assigned_to', 'created_by').distinct()

    status_filter   = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    project_filter  = request.GET.get('project')
    if status_filter:   task_qs = task_qs.filter(status=status_filter)
    if priority_filter: task_qs = task_qs.filter(priority=priority_filter)
    if project_filter:  task_qs = task_qs.filter(project_id=project_filter)

    if _is_admin(request.user):
        project_qs = Project.objects.all()
    else:
        project_qs = (Project.objects.filter(members=request.user) |
                      Project.objects.filter(owner=request.user)).distinct()

    all_users = User.objects.select_related('profile').all()

    if request.method == 'POST':
        if not _is_admin(request.user):
            messages.error(request, 'Только администратор может создавать задачи.')
            return redirect('tasks')
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        project_id  = request.POST.get('project')
        assigned_id = request.POST.get('assigned_to')
        priority    = request.POST.get('priority', 'medium')
        due_date    = request.POST.get('due_date') or None
        status      = request.POST.get('status', 'todo')
        if title and project_id:
            project  = get_object_or_404(Project, id=project_id)
            assigned = User.objects.filter(id=assigned_id).first() if assigned_id else None
            task = Task.objects.create(
                title=title, description=description, project=project,
                created_by=request.user, assigned_to=assigned,
                priority=priority, status=status, due_date=due_date,
            )
            _hist(task, request.user,
                  f'опубликовал(а) задачу «{task.title}» в проекте «{project.name}»', 'plus')
            messages.success(request, f'Задача «{task.title}» создана.')
            return redirect('task_detail', task_id=task.id)
        else:
            messages.error(request, 'Укажите название и проект.')

    return render(request, 'tasks.html', {
        'tasks': task_qs,
        'projects': project_qs,
        'all_users': all_users,
        'is_admin': _is_admin(request.user),
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_project': project_filter,
    })


# ─── task detail ────────────────────────────────────────────

@login_required
def task_detail(request, task_id):
    # Получаем задачу
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Прогресс
        if action == 'progress':
            old_progress = task.progress
            task.progress = int(request.POST.get('progress', 0) or 0)
            task.save(update_fields=['progress', 'updated_at'])
            _hist(task, request.user, f'обновил(а) прогресс: {old_progress}% → {task.progress}%', 'chart-line')
            messages.success(request, f'Прогресс сохранён: {task.progress}%')
            return redirect('task_detail', task_id=task.id)

        # Комментарий
        if action == 'comment':
            content = request.POST.get('content', '').strip()
            if content:
                Comment.objects.create(task=task, author=request.user, content=content)
                _hist(task, request.user, 'добавил(а) комментарий', 'comment')
                messages.success(request, 'Комментарий добавлен.')
            return redirect('task_detail', task_id=task.id)

        # Удаление комментария
        if action == 'delete_comment':
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, task=task)
            if comment.author == request.user or _is_admin(request.user):
                preview = comment.content[:40] + ('…' if len(comment.content) > 40 else '')
                comment.delete()
                _hist(task, request.user, f'удалил(а) комментарий: «{preview}»', 'trash-alt')
            return redirect('task_detail', task_id=task.id)

        # Остальные действия (update, delete, upload и т.д.) — оставляем как были
        # (если хочешь, могу упростить и их тоже)

    # При GET (и после редиректа) загружаем всё заново
    task = get_object_or_404(
        Task.objects.select_related('project', 'assigned_to', 'created_by'),
        id=task_id,
    )

    comments = task.comments.select_related('author').order_by('created_at').all()

    related_ids = task.related_tasks.values_list('related_id', flat=True)
    all_users   = User.objects.select_related('profile').all()
    other_tasks = Task.objects.filter(project=task.project).exclude(id=task.id).exclude(id__in=related_ids)

    return render(request, 'task_detail.html', {
        'task':            task,
        'comments':        comments,
        'files':           task.files.select_related('uploaded_by').all(),
        'history':         task.history.select_related('user').all(),
        'related_tasks':   task.related_tasks.select_related('related').all(),
        'all_users':       all_users,
        'other_tasks':     other_tasks,
        'is_admin':        _is_admin(request.user),
        'status_choices':  Task.STATUS_CHOICES,
        'priority_choices':Task.PRIORITY_CHOICES,
    })

@login_required
def download_file(request, file_id):
    tf = get_object_or_404(TaskFile, id=file_id)
    return FileResponse(tf.file.open('rb'), as_attachment=True, filename=tf.original_name)


@login_required
def team(request):
    employees = User.objects.select_related('profile').filter(profile__role=Profile.Role.EMPLOYEE)
    admins    = User.objects.select_related('profile').filter(profile__role=Profile.Role.ADMIN)
    return render(request, 'team.html', {'employees': employees, 'admins': admins})