"""Test suite for the `users` app."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class TestProfileModel(TestCase):
    """Tests for profile helpers."""

    def test_has_admin_false_by_default(self):
        self.assertFalse(Profile.has_admin())

    def test_has_admin_true_when_admin_exists(self):
        user = User.objects.create_user(username='admin1', password='pass1234')
        user.profile.role = Profile.Role.ADMIN
        user.profile.save()
        self.assertTrue(Profile.has_admin())


class TestUserViewsSmoke(TestCase):
    """Smoke tests for auth endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username='employee1', password='pass1234')

    def test_login_page_is_available(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_page_works_for_logged_user(self):
        self.client.login(username='employee1', password='pass1234')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
