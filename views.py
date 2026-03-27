from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from .models import Project, Task, Comment, TaskFile, TaskHistory, UserRole
from .forms import ProjectForm, TaskForm, CommentForm, TaskFileForm


def get_user_role(user):
    try:
        return user.role.role
    except Exception:
        return 'worker'


def can_manage_project(user, project):
    role = get_user_role(user)
    return role in ('admin', 'manager') and (role == 'admin' or project.owner == user)


def index(request):
    return render(request, "index.html")


# ── Projects ──────────────────────────────────────────────────────────────────

@login_required
def projects(request):
    role = get_user_role(request.user)
    if role == 'admin':
        project_list = Project.objects.all().order_by('-created_at')
    elif role == 'manager':
        project_list = Project.objects.filter(owner=request.user).order_by('-created_at')
    else:
        project_list = request.user.projects.all().order_by('-created_at')

    # filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    if status_filter:
        project_list = project_list.filter(status=status_filter)
    if priority_filter:
        project_list = project_list.filter(priority=priority_filter)

    form = ProjectForm()
    # limit members to workers for manager
    if role == 'manager':
        form.fields['members'].queryset = User.objects.filter(role__role='worker')
    elif role == 'admin':
        form.fields['members'].queryset = User.objects.exclude(id=request.user.id)

    return render(request, 'projects.html', {
        'project_list': project_list,
        'form': form,
        'role': role,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    })


@login_required
def create_project(request):
    role = get_user_role(request.user)
    if role not in ('admin', 'manager'):
        messages.error(request, 'Недостаточно прав.')
        return redirect('projects')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()
            messages.success(request, f'Проект «{project.name}» создан.')
            return redirect('projects')
        else:
            messages.error(request, 'Проверьте введённые данные.')
            return redirect('projects')
    return redirect('projects')


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_manage_project(request.user, project):
        messages.error(request, 'Нет прав для редактирования этого проекта.')
        return redirect('projects')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Проект «{project.name}» обновлён.')
        else:
            messages.error(request, 'Проверьте введённые данные.')
    return redirect('projects')


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not can_manage_project(request.user, project):
        messages.error(request, 'Нет прав для удаления этого проекта.')
        return redirect('projects')

    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Проект «{name}» удалён.')
    return redirect('projects')


# ── Tasks ─────────────────────────────────────────────────────────────────────

@login_required
def tasks(request):
    role = get_user_role(request.user)
    if role == 'admin':
        task_list = Task.objects.select_related('project', 'assigned_to', 'created_by').all()
    elif role == 'manager':
        task_list = Task.objects.filter(created_by=request.user).select_related('project', 'assigned_to')
    else:
        task_list = Task.objects.filter(assigned_to=request.user).select_related('project', 'created_by')

    status_filter = request.GET.get('status', '')
    project_filter = request.GET.get('project', '')
    if status_filter:
        task_list = task_list.filter(status=status_filter)
    if project_filter:
        task_list = task_list.filter(project__id=project_filter)

    # form for creating task
    task_form = TaskForm()
    if role == 'manager':
        task_form.fields['assigned_to'].queryset = User.objects.filter(role__role='worker')
        task_form.fields['project'].queryset = Project.objects.filter(owner=request.user)
    elif role == 'admin':
        task_form.fields['assigned_to'].queryset = User.objects.filter(role__role='worker')
        task_form.fields['project'].queryset = Project.objects.all()
    else:
        task_form = None

    selected_task = None
    task_id = request.GET.get('task')
    if task_id:
        try:
            selected_task = Task.objects.get(pk=task_id)
            # access check
            if role == 'worker' and selected_task.assigned_to != request.user:
                selected_task = None
            elif role == 'manager' and selected_task.created_by != request.user and get_user_role(request.user) != 'admin':
                selected_task = None
        except Task.DoesNotExist:
            pass

    comment_form = CommentForm()
    file_form = TaskFileForm()

    projects_list = []
    if role in ('admin', 'manager'):
        if role == 'manager':
            projects_list = Project.objects.filter(owner=request.user)
        else:
            projects_list = Project.objects.all()

    return render(request, 'tasks.html', {
        'task_list': task_list,
        'task_form': task_form,
        'selected_task': selected_task,
        'comment_form': comment_form,
        'file_form': file_form,
        'role': role,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'projects_list': projects_list,
    })


@login_required
def create_task(request):
    role = get_user_role(request.user)
    if role not in ('admin', 'manager'):
        messages.error(request, 'Недостаточно прав.')
        return redirect('tasks')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            TaskHistory.objects.create(
                task=task,
                changed_by=request.user,
                change_description='Задача создана.'
            )
            messages.success(request, f'Задача «{task.title}» создана.')
        else:
            messages.error(request, 'Проверьте введённые данные.')
    return redirect('tasks')


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    role = get_user_role(request.user)

    can_edit = (
        role == 'admin' or
        (role == 'manager' and task.created_by == request.user) or
        (role == 'worker' and task.assigned_to == request.user)
    )
    if not can_edit:
        messages.error(request, 'Нет прав для редактирования этой задачи.')
        return redirect('tasks')

    if request.method == 'POST':
        old_status = task.get_status_display()
        old_title = task.title

        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated = form.save()
            changes = []
            if old_status != updated.get_status_display():
                changes.append(f'Статус изменён с «{old_status}» на «{updated.get_status_display()}».')
            if old_title != updated.title:
                changes.append(f'Название изменено с «{old_title}» на «{updated.title}».')
            if not changes:
                changes.append('Задача обновлена.')
            TaskHistory.objects.create(
                task=updated,
                changed_by=request.user,
                change_description=' '.join(changes)
            )
            messages.success(request, 'Задача обновлена.')
        else:
            messages.error(request, 'Проверьте введённые данные.')
    return redirect(f'/tasks?task={pk}')


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    role = get_user_role(request.user)

    can_delete = (
        role == 'admin' or
        (role == 'manager' and task.created_by == request.user)
    )
    if not can_delete:
        messages.error(request, 'Нет прав для удаления этой задачи.')
        return redirect('tasks')

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Задача «{title}» удалена.')
    return redirect('tasks')


@login_required
def add_comment(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    role = get_user_role(request.user)

    can_comment = (
        role == 'admin' or
        (role == 'manager' and task.created_by == request.user) or
        (role == 'worker' and task.assigned_to == request.user)
    )
    if not can_comment:
        messages.error(request, 'Нет доступа к этой задаче.')
        return redirect('tasks')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            TaskHistory.objects.create(
                task=task,
                changed_by=request.user,
                change_description='Добавлен комментарий.'
            )
            messages.success(request, 'Комментарий добавлен.')
        else:
            messages.error(request, 'Комментарий не может быть пустым.')
    return redirect(f'/tasks?task={task_pk}')


@login_required
def upload_file(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    role = get_user_role(request.user)

    can_upload = (
        role == 'admin' or
        (role == 'manager' and task.created_by == request.user) or
        (role == 'worker' and task.assigned_to == request.user)
    )
    if not can_upload:
        messages.error(request, 'Нет доступа к этой задаче.')
        return redirect('tasks')

    if request.method == 'POST':
        form = TaskFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            task_file = form.save(commit=False)
            task_file.task = task
            task_file.uploaded_by = request.user
            task_file.original_name = f.name
            task_file.file_size = f.size
            task_file.save()
            TaskHistory.objects.create(
                task=task,
                changed_by=request.user,
                change_description=f'Загружен файл «{f.name}».'
            )
            messages.success(request, f'Файл «{f.name}» загружен.')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    return redirect(f'/tasks?task={task_pk}')


@login_required
def delete_file(request, file_pk):
    task_file = get_object_or_404(TaskFile, pk=file_pk)
    task = task_file.task
    role = get_user_role(request.user)

    can_delete = (
        role == 'admin' or
        task_file.uploaded_by == request.user or
        (role == 'manager' and task.created_by == request.user)
    )
    if not can_delete:
        messages.error(request, 'Нет прав для удаления этого файла.')
        return redirect(f'/tasks?task={task.id}')

    if request.method == 'POST':
        name = task_file.original_name
        task_file.file.delete(save=False)
        task_file.delete()
        TaskHistory.objects.create(
            task=task,
            changed_by=request.user,
            change_description=f'Удалён файл «{name}».'
        )
        messages.success(request, f'Файл «{name}» удалён.')
    return redirect(f'/tasks?task={task.id}')


# ── Team ──────────────────────────────────────────────────────────────────────

@login_required
def team(request):
    role = get_user_role(request.user)
    if role == 'admin':
        workers = User.objects.filter(role__role='worker').select_related('role')
        managers = User.objects.filter(role__role='manager').select_related('role')
    elif role == 'manager':
        # show workers who are members of manager's projects
        project_ids = Project.objects.filter(owner=request.user).values_list('id', flat=True)
        worker_ids = Project.objects.filter(owner=request.user).values_list('members', flat=True)
        workers = User.objects.filter(id__in=worker_ids, role__role='worker').distinct()
        managers = User.objects.none()
    else:
        workers = User.objects.none()
        managers = User.objects.none()

    return render(request, 'team.html', {
        'workers': workers,
        'managers': managers,
        'role': role,
    })
