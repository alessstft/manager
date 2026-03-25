from django import forms
from .models import Project, Task, Comment, TaskFile

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = ['pdf', 'docx', 'png', 'jpg', 'jpeg', 'zip']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'priority', 'status', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название проекта'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('Дата окончания не может быть раньше даты начала.')
        return cleaned


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название задачи'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Написать комментарий...',
                'maxlength': 1000,
            }),
        }


class TaskFileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            if f.size > MAX_FILE_SIZE:
                raise forms.ValidationError('Файл слишком большой. Максимальный размер: 10 МБ.')
            import os
            ext = os.path.splitext(f.name)[1].lower().lstrip('.')
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f'Недопустимый формат файла. Допустимые форматы: {", ".join(ALLOWED_EXTENSIONS)}.'
                )
        return f
