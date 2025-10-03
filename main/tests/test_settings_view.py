from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from ..views import SettingsView


class SettingsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.superuser = User.objects.create_user(
            username='superuser',
            email='super@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )

    def test_settings_view_requires_login(self):
        """Test that settings view requires authentication."""
        response = self.client.get(reverse('main:settings'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_settings_view_authenticated_user(self):
        """Test that authenticated users can access settings view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Settings')
        self.assertContains(response, 'Settings injected via context processor')

    def test_settings_view_context_data(self):
        """Test that settings view provides correct context data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('page_title', response.context)
        self.assertIn('settings_categories', response.context)
        self.assertIn('environment_info', response.context)
        self.assertIn('settings', response.context)

        self.assertEqual(response.context['page_title'], 'Django Settings')

    def test_settings_view_categories_structure(self):
        """Test that settings categories are properly structured."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        categories = response.context['settings_categories']

        expected_categories = [
            'Core Django', 'Database', 'Static & Media', 'Security',
            'Session & CSRF', 'Email', 'File Upload', 'Custom Project', 'System Info'
        ]

        for category in expected_categories:
            self.assertIn(category, categories)
            self.assertIsInstance(categories[category], list)
            self.assertGreater(len(categories[category]), 0)

    def test_settings_view_environment_info(self):
        """Test that environment info is correctly provided."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        env_info = response.context['environment_info']

        self.assertIn('user', env_info)
        self.assertIn('is_staff', env_info)
        self.assertIn('is_superuser', env_info)
        self.assertIn('user_permissions', env_info)
        self.assertIn('user_groups', env_info)

        self.assertEqual(env_info['user'], self.user)
        self.assertFalse(env_info['is_staff'])
        self.assertFalse(env_info['is_superuser'])
        self.assertIsInstance(env_info['user_permissions'], list)
        self.assertIsInstance(env_info['user_groups'], list)

    def test_settings_view_staff_user_info(self):
        """Test environment info for staff user."""
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        env_info = response.context['environment_info']

        self.assertEqual(env_info['user'], self.staff_user)
        self.assertTrue(env_info['is_staff'])
        self.assertFalse(env_info['is_superuser'])

    def test_settings_view_superuser_info(self):
        """Test environment info for superuser."""
        self.client.login(username='superuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        env_info = response.context['environment_info']

        self.assertEqual(env_info['user'], self.superuser)
        self.assertTrue(env_info['is_staff'])
        self.assertTrue(env_info['is_superuser'])

    def test_settings_view_template_content(self):
        """Test that settings view template contains expected content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        # Test page structure
        self.assertContains(response, 'Django Settings')
        self.assertContains(response, 'Current User')
        self.assertContains(response, 'System Info')
        self.assertContains(response, 'Context Processor Information')

        # Test user information
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

        # Test settings categories
        self.assertContains(response, 'Core Django')
        self.assertContains(response, 'Database')
        self.assertContains(response, 'Security')
        self.assertContains(response, 'System Info')

    def test_settings_view_debug_mode_display(self):
        """Test that debug mode is properly displayed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        # Should show debug status
        self.assertContains(response, 'Debug Mode')
        # The actual value depends on settings.DEBUG

    def test_settings_view_python_version_display(self):
        """Test that Python version is displayed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertContains(response, 'Python:')
        # Should contain version number format like "3.11.7"

    def test_settings_view_django_version_display(self):
        """Test that Django version is displayed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertContains(response, 'Django:')

    def test_settings_view_environment_display(self):
        """Test that environment is displayed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertContains(response, 'Environment:')

    def test_settings_view_collapsible_sections(self):
        """Test that collapsible sections are present."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        # Should contain collapsible functionality
        self.assertContains(response, 'collapsible')
        self.assertContains(response, 'toggleCollapsible')

    def test_settings_view_context_processor_info(self):
        """Test that context processor information is displayed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertContains(response, 'Context Processor:')
        self.assertContains(response, 'main.context_processors.settings_context')
        self.assertContains(response, 'Available in all templates')

    def test_settings_view_settings_count(self):
        """Test that settings count is displayed."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:settings'))

        self.assertContains(response, 'Total Settings Exposed')

    def test_settings_view_methods(self):
        """Test that SettingsView methods work correctly."""
        view = SettingsView()

        # Test _get_settings_categories
        categories = view._get_settings_categories()
        self.assertIsInstance(categories, dict)
        self.assertIn('Core Django', categories)
        self.assertIn('Database', categories)

        # Test _get_environment_info (requires request)
        request = self.client.get('/').wsgi_request
        request.user = self.user
        view.request = request

        env_info = view._get_environment_info()
        self.assertIsInstance(env_info, dict)
        self.assertIn('user', env_info)
        self.assertIn('is_staff', env_info)
        self.assertIn('is_superuser', env_info)

    def test_settings_view_template_name(self):
        """Test that SettingsView uses correct template."""
        view = SettingsView()
        self.assertEqual(view.template_name, 'main/settings.html')

    def test_settings_view_inheritance(self):
        """Test that SettingsView inherits from correct classes."""
        from django.contrib.auth.mixins import LoginRequiredMixin
        from django.views.generic import TemplateView

        self.assertTrue(issubclass(SettingsView, LoginRequiredMixin))
        self.assertTrue(issubclass(SettingsView, TemplateView))

    def test_settings_view_with_different_users(self):
        """Test settings view with different user types."""
        users = [
            (self.user, False, False),
            (self.staff_user, True, False),
            (self.superuser, True, True)
        ]

        for user, is_staff, is_superuser in users:
            with self.subTest(user=user.username):
                self.client.login(username=user.username, password='testpass123')
                response = self.client.get(reverse('main:settings'))

                self.assertEqual(response.status_code, 200)

                env_info = response.context['environment_info']
                self.assertEqual(env_info['is_staff'], is_staff)
                self.assertEqual(env_info['is_superuser'], is_superuser)
