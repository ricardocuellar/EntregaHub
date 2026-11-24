from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from accounts.models import User


@override_settings(DEBUG=True)
class SeedDemoTests(TestCase):
    def run_seed(self):
        output = StringIO()
        call_command('seed_demo', stdout=output)
        return output.getvalue()

    @patch.dict('os.environ', {'DEMO_PASSWORD': 'Ficticia-inicial-123!'})
    def test_two_runs_preserve_existing_accounts_and_changed_password(self):
        output = self.run_seed()
        expected = {
            'admin.demo': (User.Role.ADMIN, 'Ana'),
            'colaborador.demo': (User.Role.COLLABORATOR, 'Leo'),
            'cliente.demo': (User.Role.CLIENT, 'Mara'),
        }
        self.assertEqual(User.objects.count(), 3)
        for user in User.objects.all():
            self.assertEqual((user.role, user.first_name), expected[user.username])
            self.assertTrue(user.check_password('Ficticia-inicial-123!'))
            self.assertFalse(user.is_superuser)
            self.assertFalse(user.is_staff)

        user = User.objects.get(username='cliente.demo')
        user.set_password('Ficticia-cambiada-456!')
        user.role = User.Role.COLLABORATOR
        user.first_name = 'Nombre editado'
        user.email = 'ficticio@example.test'
        user.is_active = False
        user.save()
        before = list(User.objects.order_by('pk').values())

        with patch.dict('os.environ', {'DEMO_PASSWORD': 'Ficticia-segunda-789!'}):
            output += self.run_seed()

        self.assertEqual(list(User.objects.order_by('pk').values()), before)
        user.refresh_from_db()
        self.assertTrue(user.check_password('Ficticia-cambiada-456!'))
        self.assertIn('Cuentas creadas: 0', output)
        for secret in ('Ficticia-inicial-123!', 'Ficticia-cambiada-456!',
                       'Ficticia-segunda-789!', user.password):
            self.assertNotIn(secret, output)

    @override_settings(DEBUG=False)
    @patch.dict('os.environ', {'DEMO_PASSWORD': 'Ficticia-inicial-123!'})
    def test_rejects_outside_debug(self):
        with self.assertRaisesMessage(CommandError, 'DEBUG=True'):
            self.run_seed()
        self.assertFalse(User.objects.exists())

    def test_rejects_missing_or_blank_password(self):
        for environment in ({}, {'DEMO_PASSWORD': ''}, {'DEMO_PASSWORD': '   '}):
            with self.subTest(environment=environment):
                with patch.dict('os.environ', environment, clear=True):
                    with self.assertRaisesMessage(CommandError, 'DEMO_PASSWORD'):
                        self.run_seed()
                self.assertFalse(User.objects.exists())

    @patch.dict('os.environ', {'DEMO_PASSWORD': 'Ficticia-inicial-123!'})
    def test_rolls_back_all_accounts_on_failure(self):
        original = User.set_password

        def fail_on_second_account(user, password):
            if user.username == 'colaborador.demo':
                raise RuntimeError('Fallo simulado')
            original(user, password)

        with patch.object(User, 'set_password', fail_on_second_account):
            with self.assertRaisesMessage(RuntimeError, 'Fallo simulado'):
                self.run_seed()
        self.assertFalse(User.objects.exists())
