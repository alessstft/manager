"""! @file models.py
@brief User profile model and role helpers.
"""

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """! @brief Extended account profile with application role."""
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        EMPLOYEE = 'employee', 'Сотрудник'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        """! @brief Returns profile label for admin UI."""
        return f'{self.user.username} Profile'

    @classmethod
    def has_admin(cls):
        """! @brief Checks if at least one admin account exists."""
        return cls.objects.filter(role=cls.Role.ADMIN).exists()

    def display_name(self):
        """! @brief Returns full name or username fallback."""
        full = self.user.get_full_name().strip()
        if full:
            return full
        return self.user.username
