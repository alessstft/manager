from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
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
        return f'{self.user.username} Profile'

    @classmethod
    def has_admin(cls):
        return cls.objects.filter(role=cls.Role.ADMIN).exists()

    def display_name(self):
        full = self.user.get_full_name().strip()
        if full:
            return full
        return self.user.username
