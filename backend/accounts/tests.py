from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.conf import settings
from django.test import Client, TestCase, override_settings

from accounts.models import User


class SessionApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'Clave-ficticia-123!'
        cls.user = User.objects.create_user(
            username='sesion.demo', password=cls.password,
            first_name='Ana', last_name='Demo', role=User.Role.COLLABORATOR,
            email='privado@example.test', is_staff=True,
        )
        User.objects.create_user(username='otra.demo', password=cls.password)

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def assert_not_cached(self, response):
        for directive in ('no-cache', 'no-store', 'must-revalidate', 'private'):
            self.assertIn(directive, response.headers['Cache-Control'])
        self.assertIn('Expires', response.headers)

    def csrf(self):
        response = self.client.get('/api/auth/csrf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'csrfToken'})
        self.assert_not_cached(response)
        return response.json()['csrfToken']

    def login(self, token, **extra):
        return self.client.post(
            '/api/auth/login/',
            {'username': self.user.username, 'password': self.password},
            content_type='application/json', HTTP_X_CSRFTOKEN=token, **extra,
        )

    def authenticated_token(self):
        response = self.login(self.csrf())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'csrfToken', 'user'})
        self.assert_not_cached(response)
        return response.json()['csrfToken']

    def test_anonymous_login_without_csrf_is_rejected(self):
        response = self.client.post('/api/auth/login/', {
            'username': self.user.username, 'password': self.password,
        }, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assert_not_cached(response)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)

    def test_anonymous_login_with_cookie_but_without_token_is_rejected(self):
        self.csrf()
        response = self.client.post('/api/auth/login/', {
            'username': self.user.username, 'password': self.password,
        }, content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_foreign_origin_is_rejected(self):
        response = self.login(self.csrf(), HTTP_ORIGIN='https://ajeno.example.test')
        self.assertEqual(response.status_code, 403)
        self.assert_not_cached(response)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)

    def test_login_rotates_csrf_and_sets_httponly_session(self):
        token = self.csrf()
        old_cookie = self.client.cookies[settings.CSRF_COOKIE_NAME].value
        response = self.login(token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'csrfToken', 'user'})
        self.assertEqual(response.json()['user'], {
            'id': self.user.pk, 'username': self.user.username,
            'name': 'Ana Demo', 'role': User.Role.COLLABORATOR,
        })
        self.assertEqual(response.json()['user'],
                         self.client.get('/api/auth/me/').json()['user'])
        self.assert_not_cached(response)
        self.assertNotEqual(response.json()['csrfToken'], token)
        self.assertNotEqual(self.client.cookies[settings.CSRF_COOKIE_NAME].value, old_cookie)
        self.assertTrue(response.cookies[settings.SESSION_COOKIE_NAME]['httponly'])
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))

    def test_me_requires_session_and_returns_only_current_public_fields(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 403)
        self.assert_not_cached(response)
        self.authenticated_token()
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user': {
            'id': self.user.pk, 'username': self.user.username,
            'name': 'Ana Demo', 'role': User.Role.COLLABORATOR,
        }})
        self.assert_not_cached(response)

    def test_invalid_credentials_are_generic_and_do_not_create_session(self):
        token = self.csrf()
        for credentials in (
            {'username': self.user.username, 'password': 'incorrecta'},
            {'username': 'inexistente', 'password': self.password},
            {}, {'username': self.user.username},
            {'username': '', 'password': ''},
            {'username': self.user.username, 'password': ['invalida']},
        ):
            with self.subTest(credentials=credentials):
                response = self.client.post('/api/auth/login/', credentials,
                                            content_type='application/json',
                                            HTTP_X_CSRFTOKEN=token)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), {'detail': 'Credenciales incorrectas.'})
                self.assert_not_cached(response)
                self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_user_cannot_login(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        response = self.login(self.csrf())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Credenciales incorrectas.'})
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)

    def test_deactivation_blocks_existing_session(self):
        token = self.authenticated_token()
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)
        response = self.client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 403)

    def test_logout_without_token_or_with_prelogin_token_is_rejected(self):
        old_token = self.csrf()
        self.assertEqual(self.login(old_token).status_code, 200)
        for headers in ({}, {'HTTP_X_CSRFTOKEN': old_token}):
            with self.subTest(headers=headers):
                response = self.client.post('/api/auth/logout/', **headers)
                self.assertEqual(response.status_code, 403)
                self.assert_not_cached(response)
                self.assertEqual(self.client.get('/api/auth/me/').status_code, 200)

    def test_logout_requires_session_even_with_valid_csrf(self):
        response = self.client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=self.csrf())
        self.assertEqual(response.status_code, 403)
        self.assert_not_cached(response)

    def test_logout_rotates_csrf_ends_session_and_allows_new_login(self):
        token = self.authenticated_token()
        old_session = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        old_cookie = self.client.cookies[settings.CSRF_COOKIE_NAME].value
        response = self.client.post('/api/auth/logout/', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'csrfToken'})
        self.assert_not_cached(response)
        self.assertNotEqual(response.json()['csrfToken'], token)
        self.assertNotEqual(self.client.cookies[settings.CSRF_COOKIE_NAME].value, old_cookie)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 403)
        # Replaying the former session cookie must also fail.
        replay = Client(enforce_csrf_checks=True)
        replay.cookies[settings.SESSION_COOKIE_NAME] = old_session
        self.assertEqual(replay.get('/api/auth/me/').status_code, 403)
        self.assertEqual(self.client.post('/api/auth/logout/',
                         HTTP_X_CSRFTOKEN=response.json()['csrfToken']).status_code, 403)
        self.assertEqual(self.login(response.json()['csrfToken']).status_code, 200)


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
