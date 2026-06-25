from django.core.management.base import BaseCommand

from billing.services.backup_service import create_backup


class Command(BaseCommand):

    help = "Create HomeDen backup"

    def handle(self, *args, **kwargs):

        path = create_backup()

        self.stdout.write(
            self.style.SUCCESS(
                f"Backup created successfully\n{path}"
            )
        )