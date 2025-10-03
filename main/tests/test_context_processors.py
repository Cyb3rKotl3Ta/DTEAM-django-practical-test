from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.template import Context, Template
from django.conf import settings

from ..context_processors import settings_context


class SettingsContextProcessorTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_settings_context_processor_returns_dict(self):
        """Test that settings_context processor returns a dictionary."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)

        self.assertIsInstance(context, dict)
        self.assertIn('settings', context)

    def test_settings_context_contains_core_settings(self):
        """Test that settings context contains core Django settings."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        # Test core Django settings
        self.assertIn('DEBUG', settings_dict)
        self.assertIn('SECRET_KEY', settings_dict)
        self.assertIn('ALLOWED_HOSTS', settings_dict)
        self.assertIn('TIME_ZONE', settings_dict)
        self.assertIn('LANGUAGE_CODE', settings_dict)
        self.assertIn('USE_I18N', settings_dict)
        self.assertIn('USE_TZ', settings_dict)

    def test_settings_context_contains_database_settings(self):
        """Test that settings context contains database settings."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('DATABASES', settings_dict)
        self.assertIn('default', settings_dict['DATABASES'])
        self.assertIn('ENGINE', settings_dict['DATABASES']['default'])
        self.assertIn('NAME', settings_dict['DATABASES']['default'])

    def test_settings_context_contains_static_media_settings(self):
        """Test that settings context contains static and media settings."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('STATIC_URL', settings_dict)
        self.assertIn('MEDIA_URL', settings_dict)
        self.assertIn('STATIC_ROOT', settings_dict)
        self.assertIn('MEDIA_ROOT', settings_dict)

    def test_settings_context_contains_security_settings(self):
        """Test that settings context contains security settings."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('SECURE_SSL_REDIRECT', settings_dict)
        self.assertIn('SECURE_HSTS_SECONDS', settings_dict)
        self.assertIn('X_FRAME_OPTIONS', settings_dict)
        self.assertIn('SESSION_COOKIE_SECURE', settings_dict)
        self.assertIn('CSRF_COOKIE_SECURE', settings_dict)

    def test_settings_context_contains_email_settings(self):
        """Test that settings context contains email settings."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('EMAIL_BACKEND', settings_dict)
        self.assertIn('EMAIL_HOST', settings_dict)
        self.assertIn('EMAIL_PORT', settings_dict)
        self.assertIn('EMAIL_USE_TLS', settings_dict)
        self.assertIn('EMAIL_USE_SSL', settings_dict)

    def test_settings_context_contains_custom_project_settings(self):
        """Test that settings context contains custom project settings."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('DJANGO_ENV', settings_dict)
        self.assertIn('REQUEST_LOG_EXCLUDED_PATHS', settings_dict)
        self.assertIn('REQUEST_LOG_EXCLUDED_METHODS', settings_dict)
        self.assertIn('REQUEST_LOG_AUTHENTICATED_ONLY', settings_dict)

    def test_settings_context_contains_system_info(self):
        """Test that settings context contains system information."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('PYTHON_VERSION', settings_dict)
        self.assertIn('DJANGO_VERSION', settings_dict)
        self.assertIn('CURRENT_TIME', settings_dict)
        self.assertIn('SERVER_NAME', settings_dict)
        self.assertIn('SERVER_PORT', settings_dict)
        self.assertIn('HTTP_HOST', settings_dict)
        self.assertIn('REQUEST_METHOD', settings_dict)
        self.assertIn('PATH_INFO', settings_dict)
        self.assertIn('REMOTE_ADDR', settings_dict)
        self.assertIn('HTTP_USER_AGENT', settings_dict)

    def test_settings_context_secret_key_masked(self):
        """Test that SECRET_KEY is masked for security."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        secret_key = settings_dict['SECRET_KEY']
        if secret_key:
            self.assertTrue(secret_key.endswith('...'))
            self.assertLess(len(secret_key), len(settings.SECRET_KEY))

    def test_settings_context_installed_apps_included(self):
        """Test that INSTALLED_APPS is included in settings context."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('INSTALLED_APPS', settings_dict)
        self.assertIsInstance(settings_dict['INSTALLED_APPS'], list)
        self.assertIn('django.contrib.admin', settings_dict['INSTALLED_APPS'])

    def test_settings_context_middleware_included(self):
        """Test that MIDDLEWARE is included in settings context."""
        request = self.factory.get('/')
        request.user = self.user

        context = settings_context(request)
        settings_dict = context['settings']

        self.assertIn('MIDDLEWARE', settings_dict)
        self.assertIsInstance(settings_dict['MIDDLEWARE'], list)
        self.assertIn('django.middleware.security.SecurityMiddleware', settings_dict['MIDDLEWARE'])

    def test_settings_context_works_in_template(self):
        """Test that settings context works in Django templates."""
        request = self.factory.get('/')
        request.user = self.user

        # Create a simple template that uses settings
        template_string = """
        {% load settings_extras %}
        <div>
            <p>DEBUG: {{ settings.DEBUG }}</p>
            <p>TIME_ZONE: {{ settings.TIME_ZONE }}</p>
            <p>PYTHON_VERSION: {{ settings.PYTHON_VERSION }}</p>
        </div>
        """

        template = Template(template_string)
        context = Context(settings_context(request))

        rendered = template.render(context)

        self.assertIn('DEBUG:', rendered)
        self.assertIn('TIME_ZONE:', rendered)
        self.assertIn('PYTHON_VERSION:', rendered)
        self.assertIn(str(settings.DEBUG), rendered)
        self.assertIn(settings.TIME_ZONE, rendered)

    def test_settings_context_with_different_request_methods(self):
        """Test that settings context works with different HTTP methods."""
        methods = ['GET', 'POST', 'PUT', 'DELETE']

        for method in methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())('/')
                request.user = self.user

                context = settings_context(request)
                settings_dict = context['settings']

                self.assertEqual(settings_dict['REQUEST_METHOD'], method)

    def test_settings_context_with_different_paths(self):
        """Test that settings context works with different paths."""
        paths = ['/', '/admin/', '/api/', '/settings/']

        for path in paths:
            with self.subTest(path=path):
                request = self.factory.get(path)
                request.user = self.user

                context = settings_context(request)
                settings_dict = context['settings']

                self.assertEqual(settings_dict['PATH_INFO'], path)

    def test_settings_context_anonymous_user(self):
        """Test that settings context works with anonymous users."""
        request = self.factory.get('/')
        request.user = User()  # Anonymous user

        context = settings_context(request)

        self.assertIsInstance(context, dict)
        self.assertIn('settings', context)
        settings_dict = context['settings']
        self.assertIn('DEBUG', settings_dict)
