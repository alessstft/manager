"""Test suite for the `new` app."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Project, Task


class TestProjectModel(TestCase):
    """Tests for project aggregation helpers."""

    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass1234')
        self.project = Project.objects.create(name='Alpha', owner=self.owner)

    def test_progress_is_zero_without_tasks(self):
        self.assertEqual(self.project.progress(), 0)

    def test_progress_counts_only_done_tasks(self):
        Task.objects.create(
            title='Done task',
            project=self.project,
            created_by=self.owner,
            status='done',
        )
        Task.objects.create(
            title='Todo task',
            project=self.project,
            created_by=self.owner,
            status='todo',
        )
        self.assertEqual(self.project.task_count(), 2)
        self.assertEqual(self.project.done_count(), 1)
        self.assertEqual(self.project.progress(), 50)


class TestTaskModel(TestCase):
    """Tests for task helper methods."""

    def setUp(self):
        owner = User.objects.create_user(username='owner2', password='pass1234')
        project = Project.objects.create(name='Beta', owner=owner)
        self.task = Task.objects.create(
            title='My task',
            project=project,
            created_by=owner,
            status='in_progress',
            priority='high',
        )

    def test_status_and_priority_colors(self):
        self.assertEqual(self.task.status_color(), 'info')
        self.assertEqual(self.task.priority_color(), 'danger')


class TestNewViewsSmoke(TestCase):
    """Smoke tests for app routes."""

    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass1234')

    def test_home_page_is_available(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_projects_requires_login(self):
        response = self.client.get(reverse('projects'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_logged_in_user_can_create_project(self):
        self.client.login(username='u1', password='pass1234')
        response = self.client.post(
            reverse('projects'),
            {'name': 'New project', 'description': 'desc', 'priority': 'medium'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New project', owner=self.user).exists())
