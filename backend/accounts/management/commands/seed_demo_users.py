import os

from django.core.management.base import BaseCommand

from accounts.models import Role, User

DEMO_USERS = [
    ("alice", Role.SUBMITTER),
    ("bob", Role.SUBMITTER),
    ("rita", Role.REVIEWER),
]


class Command(BaseCommand):
    help = "Create demo users (idempotent). Password: DEMO_PASSWORD env var, default 'demo-pass'."

    def handle(self, *args, **options):
        password = os.environ.get("DEMO_PASSWORD", "demo-pass")
        for username, role in DEMO_USERS:
            user, created = User.objects.get_or_create(username=username, defaults={"role": role})
            user.role = role
            user.set_password(password)
            user.save()
            self.stdout.write(f"{'created' if created else 'updated'} {username} ({role})")
