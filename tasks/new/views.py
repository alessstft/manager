import os
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Avg, Q
from django.conf import settings
from django.db.utils import DatabaseError, OperationalError

from users.models import Profile
from .models import Comment, HistoryEntry, Project, RelatedTask, Task, TaskFile


# ─── helpers ────────────────────────────────────────────────

def _is_admin(user):
    try:
        return user.profile.role == Profile.Role.ADMIN
    except Profile.DoesNotExist:
        return False


def _can_access_task(user, task):
    if _is_admin(user):
        return True
    if task.assigned_to_id == user.id or task.created_by_id == user.id:
        return True
    p = task.project
    return (
        p.members.filter(pk=user.pk).exists()
        or p.owner_id == user.id
        or p.assigned_to_id == user.id
    )


def _uname(user):
    return user.get_full_name().strip() or user.username

def _hist(task, user, action, icon='edit'):
    HistoryEntry.objects.create(task=task, user=user, action=action, icon=icon)


def _new_app_db_ready():
    """Проекты с участниками (M2M → new_project_members) и задачи — основные таблицы приложения new."""
    try:
        Project.members.through.objects.exists()
        Task.objects.exists()
        return True
    except (OperationalError, DatabaseError):
        return False


def _db_schema_setup_response(request):
    ctx = {}
    eng = settings.DATABASES['default'].get('ENGINE', '')
    if 'sqlite' in eng:
        ctx['sqlite_path'] = str(settings.DATABASES['default'].get('NAME', ''))
    return render(request, 'schema_setup.html', ctx)


def require_new_app_db(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not _new_app_db_ready():
            return _db_schema_setup_response(request)
        return view_func(request, *args, **kwargs)

    return _wrapped


# ─── index ──────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html', {'admin_registered': Profile.has_admin()})


# ─── projects ───────────────────────────────────────────────

@login_required
@require_new_app_db
def projects(request):
    if _is_admin(request.user):
        qs = Project.objects.all()
    else:
        qs = (
            Project.objects.filter(members=request.user)
            | Project.objects.filter(owner=request.user)
            | Project.objects.filter(assigned_to=request.user)
        ).distinct()

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

    priority_filter = request.GET.getlist('priority')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if priority_filter:
        qs = qs.filter(priority__in=priority_filter)
    if date_from:
        qs = qs.filter(end_date__gte=date_from)
    if date_to:
        qs = qs.filter(end_date__lte=date_to)

    return render(request, 'projects.html', {
        'projects': qs,
        'all_users': all_users,
        'is_admin': _is_admin(request.user),
        'selected_priorities': priority_filter,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
@require_new_app_db
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


@login_required
@require_new_app_db
@require_POST
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user and not _is_admin(request.user):
        messages.error(request, 'Нет прав для редактирования.')
        return redirect('projects')
    name = request.POST.get('name', '').strip()
    if not name:
        messages.error(request, 'Укажите название проекта.')
        return redirect('projects')
    project.name = name
    project.description = request.POST.get('description', '').strip()
    project.priority = request.POST.get('priority', 'medium')
    project.start_date = request.POST.get('start_date') or None
    project.end_date = request.POST.get('end_date') or None
    assigned_id = request.POST.get('assigned_to') or None
    from django.contrib.auth.models import User as U
    project.assigned_to = U.objects.filter(id=assigned_id).first() if assigned_id else None
    project.save()
    project.members.add(project.owner)
    if project.assigned_to_id:
        project.members.add(project.assigned_to)
    messages.success(request, f'Проект «{project.name}» обновлён.')
    return redirect('projects')


@login_required
@require_new_app_db
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        assigned_id = request.POST.get('assigned_to') or None
        if name:
            from django.contrib.auth.models import User as U
            assigned = U.objects.filter(id=assigned_id).first() if assigned_id else None
            project = Project.objects.create(
                name=name, description=description, priority=priority,
                start_date=start_date, end_date=end_date, owner=request.user,
                assigned_to=assigned,
            )
            # Список проектов для сотрудника строится по M2M members, а не по assigned_to
            project.members.add(request.user)
            if assigned:
                project.members.add(assigned)
            messages.success(request, f'Проект «{name}» создан.')
        else:
            messages.error(request, 'Укажите название проекта.')
    return redirect('projects')


# ─── tasks list ─────────────────────────────────────────────

@login_required
@require_new_app_db
def tasks_list(request):
    if _is_admin(request.user):
        task_qs = Task.objects.select_related('project', 'assigned_to', 'created_by').all()
    else:
        task_qs = Task.objects.filter(
            Q(assigned_to=request.user)
            | Q(created_by=request.user)
            | Q(project__members=request.user)
            | Q(project__owner=request.user)
            | Q(project__assigned_to=request.user)
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
        project_qs = (
            Project.objects.filter(members=request.user)
            | Project.objects.filter(owner=request.user)
            | Project.objects.filter(assigned_to=request.user)
        ).distinct()

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

    current_project_id = None
    if project_filter:
        try:
            current_project_id = int(project_filter)
        except (TypeError, ValueError):
            pass

    return render(request, 'tasks.html', {
        'tasks': task_qs,
        'projects': project_qs,
        'all_users': all_users,
        'is_admin': _is_admin(request.user),
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_project_id': current_project_id,
    })


# ─── task detail ────────────────────────────────────────────

@login_required
@require_new_app_db
def task_detail(request, task_id):
    task = get_object_or_404(
        Task.objects.select_related('project', 'assigned_to', 'created_by'),
        id=task_id,
    )

    if not _can_access_task(request.user, task):
        messages.error(request, 'Нет доступа к этой задаче.')
        return redirect('tasks')

    if request.method == 'POST':
        action = request.POST.get('action')

        # === 1. Только назначенный, создатель или админ могут менять прогресс ===
        if action == 'progress':
            if not (
                (task.assigned_to and task.assigned_to.id == request.user.id) or
                (task.created_by and task.created_by.id == request.user.id) or
                _is_admin(request.user)
            ):
                messages.error(request, "Только назначенный исполнитель, создатель задачи или администратор может изменять прогресс.")
                return redirect('task_detail', task_id=task.id)

            old_progress = task.progress
            task.progress = int(request.POST.get('progress', 0) or 0)
            task.save(update_fields=['progress', 'updated_at'])
            _hist(task, request.user, f'обновил(а) прогресс: {old_progress}% → {task.progress}%', 'chart-line')
            messages.success(request, f'Прогресс сохранён: {task.progress}%')
            return redirect('task_detail', task_id=task.id)

        # === 2. Сохранение связанных задач ===
        if action == 'related_tasks' or 'related_tasks' in request.POST:
            related_ids = request.POST.getlist('related_tasks')
            RelatedTask.objects.filter(task=task).delete()
            added = 0
            for rid_str in related_ids:
                if rid_str:
                    try:
                        rid = int(rid_str)
                        if rid != task.id:
                            RelatedTask.objects.get_or_create(task=task, related_id=rid)
                            added += 1
                    except ValueError:
                        pass
            _hist(task, request.user, f'обновил(а) связанные задачи ({added} шт.)', 'link')
            messages.success(request, f'Связанные задачи обновлены ({added} шт.).')
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

    # GET — перезагружаем задачу и рендерим страницу
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
        'priority_choices': Task.PRIORITY_CHOICES,
    })
@login_required
@require_new_app_db
def download_file(request, file_id):
    tf = get_object_or_404(TaskFile.objects.select_related('task__project'), id=file_id)
    if not _can_access_task(request.user, tf.task):
        messages.error(request, 'Нет доступа к файлу.')
        return redirect('tasks')
    return FileResponse(tf.file.open('rb'), as_attachment=True, filename=tf.original_name)


@login_required
def team(request):
    employees = User.objects.select_related('profile').filter(profile__role=Profile.Role.EMPLOYEE)
    admins    = User.objects.select_related('profile').filter(profile__role=Profile.Role.ADMIN)
    return render(request, 'team.html', {'employees': employees, 'admins': admins})


@login_required
@require_new_app_db
def workload(request):
    """Актуальная нагрузка по задачам и просрочки (данные из БД)."""
    today = timezone.localdate()
    is_admin = _is_admin(request.user)

    if is_admin:
        users_qs = User.objects.select_related('profile').all().order_by('profile__role', 'username')
    else:
        users_qs = User.objects.filter(pk=request.user.pk).select_related('profile')

    employee_rows = []
    for u in users_qs:
        try:
            prof = u.profile
        except Profile.DoesNotExist:
            continue

        # Все незавершённые задачи, назначенные на сотрудника (в т.ч. из админки), без фильтра по участию в проекте
        active_qs = Task.objects.filter(assigned_to=u).exclude(status='done')
        active_count = active_qs.count()
        overdue_assigned = active_qs.filter(due_date__isnull=False, due_date__lt=today).count()
        avg_prog = active_qs.aggregate(v=Avg('progress'))['v']
        avg_prog = int(round(avg_prog or 0))
        load_pct = min(100, active_count * 12 + avg_prog // 2)

        active_tasks_list = list(
            active_qs.select_related('project').order_by('project__name', 'title')[:40]
        )
        project_names = sorted({t.project.name for t in active_tasks_list})

        employee_rows.append({
            'name': prof.display_name(),
            'role_label': prof.get_role_display(),
            'active_count': active_count,
            'overdue_count': overdue_assigned,
            'avg_progress': avg_prog,
            'load_percent': load_pct,
            'project_names': project_names,
            'active_tasks': active_tasks_list,
        })

    overdue_qs = (
        Task.objects.filter(due_date__isnull=False, due_date__lt=today)
        .exclude(status='done')
        .select_related('project', 'assigned_to', 'assigned_to__profile')
        .order_by('due_date')
    )
    if not is_admin:
        overdue_qs = overdue_qs.filter(assigned_to=request.user)

    delay_rows = []
    for t in overdue_qs:
        if t.assigned_to_id:
            try:
                assignee = t.assigned_to.profile.display_name()
            except Profile.DoesNotExist:
                assignee = t.assigned_to.username
        else:
            assignee = 'Не назначена'
        desc = (t.description or '').strip()
        reason = desc if desc else 'Не указано — добавьте пояснение в описании задачи.'
        if len(reason) > 400:
            reason = reason[:400] + '…'
        delay_rows.append({
            'task': t,
            'assignee': assignee,
            'days_late': (today - t.due_date).days,
            'reason': reason,
        })

    return render(request, 'workload.html', {
        'employee_rows': employee_rows,
        'delay_rows': delay_rows,
        'is_admin': is_admin,
        'today': today,
    })