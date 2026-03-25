import os
import sys
from pathlib import Path


def main() -> None:
    # Ensure Django knows which settings module to use.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tasks.settings")

    # Make sure `import new` / `import users` works from the project root.
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

