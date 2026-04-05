from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import Profile


class Command(BaseCommand):
    help = (
        "Создаёт локальных пользователей для входа: администратор (и по желанию сотрудник). "
        "Только для разработки."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default="admin",
            help="Логин администратора (по умолчанию: admin).",
        )
        parser.add_argument(
            "--password",
            default="devpass123",
            help="Пароль администратора (по умолчанию: devpass123).",
        )
        parser.add_argument(
            "--employee",
            action="store_true",
            help="Также создать сотрудника (worker / тот же пароль, если не задано иное).",
        )
        parser.add_argument(
            "--employee-username",
            default="worker",
            help="Логин сотрудника (по умолчанию: worker).",
        )
        parser.add_argument(
            "--employee-password",
            default=None,
            help="Пароль сотрудника (по умолчанию как у администратора).",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Если пользователь уже есть — обновить пароль и роль.",
        )

    def handle(self, *args, **options):
        admin_username = options["username"]
        admin_password = options["password"]
        reset = options["reset"]

        user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": f"{admin_username}@example.local",
                "first_name": "Dev",
                "last_name": "Admin",
            },
        )
        if not created and not reset:
            self.stdout.write(
                self.style.WARNING(
                    f'Администратор «{admin_username}» уже есть (пароль не менялся). '
                    "Добавь --reset чтобы обновить пароль и роль."
                )
            )
        else:
            if not created and reset:
                user.email = user.email or f"{admin_username}@example.local"
                user.first_name = user.first_name or "Dev"
                user.last_name = user.last_name or "Admin"

            user.set_password(admin_password)
            user.is_staff = True
            user.is_superuser = True
            user.save()

            profile = user.profile
            profile.role = Profile.Role.ADMIN
            profile.save()

            self.stdout.write(self.style.SUCCESS("Администратор готов:"))
            self.stdout.write(f"  логин:    {admin_username}")
            self.stdout.write(f"  пароль:   {admin_password}")

        self.stdout.write("  URL входа: /login/")

        if not options["employee"]:
            return

        ew = options["employee_username"]
        ep = options["employee_password"] or admin_password
        eu, e_created = User.objects.get_or_create(
            username=ew,
            defaults={
                "email": f"{ew}@example.local",
                "first_name": "Dev",
                "last_name": "Worker",
            },
        )
        if not e_created and not reset:
            self.stdout.write(
                self.style.WARNING(
                    f'Сотрудник «{ew}» уже есть (пароль не менялся). '
                    "Добавь --reset чтобы обновить пароль и роль."
                )
            )
            return

        if not e_created and reset:
            eu.email = eu.email or f"{ew}@example.local"
            eu.first_name = eu.first_name or "Dev"
            eu.last_name = eu.last_name or "Worker"

        eu.set_password(ep)
        eu.is_staff = False
        eu.is_superuser = False
        eu.save()
        ep_profile = eu.profile
        ep_profile.role = Profile.Role.EMPLOYEE
        ep_profile.save()
        self.stdout.write(self.style.SUCCESS("Сотрудник готов:"))
        self.stdout.write(f"  логин:    {ew}")
        self.stdout.write(f"  пароль:   {ep}")
