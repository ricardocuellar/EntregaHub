import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User


class Command(BaseCommand):
    help = 'Carga cuentas ficticias únicamente en desarrollo; conserva las existentes.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('seed_demo solo está permitido con DEBUG=True.')
        password = os.environ.get('DEMO_PASSWORD')
        if not password or not password.strip():
            raise CommandError('Configura DEMO_PASSWORD en el entorno.')

        accounts = (
            ('admin.demo', User.Role.ADMIN, 'Ana'),
            ('colaborador.demo', User.Role.COLLABORATOR, 'Leo'),
            ('cliente.demo', User.Role.CLIENT, 'Mara'),
        )
        created_count = 0
        with transaction.atomic():
            for username, role, first_name in accounts:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'role': role, 'first_name': first_name},
                )
                if created:
                    user.set_password(password)
                    user.save(update_fields=['password'])
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Cuentas creadas: {created_count}; existentes conservadas: {3 - created_count}.'
        ))
