from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from unittest.mock import patch
import time

from .models import RequestLog
from .middleware import RequestLoggingMiddleware


class RequestLogModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.request_log = RequestLog.objects.create(
            http_method='GET',
            path='/test/path/',
            query_string='param=value',
            remote_ip='127.0.0.1',
            user_agent='Test User Agent',
            user=self.user,
            response_status=200,
            response_time_ms=150,
            request_size_bytes=1024,
            response_size_bytes=2048,
            is_authenticated=True,
            is_staff=False,
            is_superuser=False
        )

    def test_str_representation(self):
        expected = f"GET /test/path/ ({self.user.username}) [200] - {self.request_log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        self.assertEqual(str(self.request_log), expected)

    def test_is_successful_property(self):
        self.assertTrue(self.request_log.is_successful)

        self.request_log.response_status = 404
        self.assertFalse(self.request_log.is_successful)

    def test_is_client_error_property(self):
        self.request_log.response_status = 404
        self.assertTrue(self.request_log.is_client_error)

        self.request_log.response_status = 200
        self.assertFalse(self.request_log.is_client_error)

    def test_is_server_error_property(self):
        self.request_log.response_status = 500
        self.assertTrue(self.request_log.is_server_error)

        self.request_log.response_status = 200
        self.assertFalse(self.request_log.is_server_error)

    def test_duration_seconds_property(self):
        self.assertEqual(self.request_log.duration_seconds, 0.15)

        self.request_log.response_time_ms = None
        self.assertIsNone(self.request_log.duration_seconds)

    def test_get_user_info(self):
        self.assertEqual(self.request_log.get_user_info(), f"{self.user.username} ({self.user.email})")

        self.request_log.user = None
        self.assertEqual(self.request_log.get_user_info(), "Anonymous")


class RequestLogManagerTestCase(TestCase):
    def setUp(self):
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

        RequestLog.objects.create(
            http_method='GET',
            path='/test/path/',
            remote_ip='127.0.0.1',
            user=self.user,
            response_status=200,
            response_time_ms=100,
            is_authenticated=True
        )

        RequestLog.objects.create(
            http_method='POST',
            path='/test/path/',
            remote_ip='192.168.1.1',
            user=self.staff_user,
            response_status=404,
            response_time_ms=2000,
            is_authenticated=True,
            is_staff=True
        )

        RequestLog.objects.create(
            http_method='GET',
            path='/anonymous/path/',
            remote_ip='10.0.0.1',
            response_status=500,
            response_time_ms=5000,
            is_authenticated=False
        )

    def test_successful_queryset(self):
        successful_logs = RequestLog.objects.successful()
        self.assertEqual(successful_logs.count(), 1)
        self.assertEqual(successful_logs.first().response_status, 200)

    def test_client_errors_queryset(self):
        client_errors = RequestLog.objects.client_errors()
        self.assertEqual(client_errors.count(), 1)
        self.assertEqual(client_errors.first().response_status, 404)

    def test_server_errors_queryset(self):
        server_errors = RequestLog.objects.server_errors()
        self.assertEqual(server_errors.count(), 1)
        self.assertEqual(server_errors.first().response_status, 500)

    def test_by_method_queryset(self):
        get_logs = RequestLog.objects.by_method('GET')
        self.assertEqual(get_logs.count(), 2)

        post_logs = RequestLog.objects.by_method('POST')
        self.assertEqual(post_logs.count(), 1)

    def test_by_user_queryset(self):
        user_logs = RequestLog.objects.by_user(self.user)
        self.assertEqual(user_logs.count(), 1)
        self.assertEqual(user_logs.first().user, self.user)

    def test_by_ip_queryset(self):
        ip_logs = RequestLog.objects.by_ip('127.0.0.1')
        self.assertEqual(ip_logs.count(), 1)
        self.assertEqual(ip_logs.first().remote_ip, '127.0.0.1')

    def test_authenticated_only_queryset(self):
        auth_logs = RequestLog.objects.authenticated_only()
        self.assertEqual(auth_logs.count(), 2)

    def test_anonymous_only_queryset(self):
        anon_logs = RequestLog.objects.anonymous_only()
        self.assertEqual(anon_logs.count(), 1)

    def test_staff_only_queryset(self):
        staff_logs = RequestLog.objects.staff_only()
        self.assertEqual(staff_logs.count(), 1)
        self.assertEqual(staff_logs.first().user, self.staff_user)

    def test_slow_requests_queryset(self):
        slow_logs = RequestLog.objects.slow_requests(threshold_ms=1000)
        self.assertEqual(slow_logs.count(), 2)

    def test_get_stats(self):
        stats = RequestLog.objects.get_stats()
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['successful_requests'], 1)
        self.assertEqual(stats['client_errors'], 1)
        self.assertEqual(stats['server_errors'], 1)
        self.assertAlmostEqual(stats['success_rate'], 33.33, places=1)
        self.assertAlmostEqual(stats['error_rate'], 66.67, places=1)

    def test_get_top_paths(self):
        top_paths = RequestLog.objects.get_top_paths()
        self.assertEqual(len(top_paths), 2)
        self.assertEqual(top_paths[0]['path'], '/test/path/')
        self.assertEqual(top_paths[0]['count'], 2)

    def test_get_top_ips(self):
        top_ips = RequestLog.objects.get_top_ips()
        self.assertEqual(len(top_ips), 3)

    def test_get_method_distribution(self):
        method_dist = RequestLog.objects.get_method_distribution()
        self.assertEqual(len(method_dist), 2)

        get_count = next(item['count'] for item in method_dist if item['http_method'] == 'GET')
        post_count = next(item['count'] for item in method_dist if item['http_method'] == 'POST')

        self.assertEqual(get_count, 2)
        self.assertEqual(post_count, 1)


class RequestLoggingMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestLoggingMiddleware(lambda r: self._mock_response())
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def _mock_response(self):
        from django.http import HttpResponse
        response = HttpResponse("Test response")
        response.status_code = 200
        return response

    def test_middleware_logs_request(self):
        request = self.factory.get('/test/path/')
        request.user = self.user

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestLog.objects.count(), 1)

        log = RequestLog.objects.first()
        self.assertEqual(log.http_method, 'GET')
        self.assertEqual(log.path, '/test/path/')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.response_status, 200)
        self.assertTrue(log.is_authenticated)

    def test_middleware_logs_anonymous_request(self):
        from django.contrib.auth.models import AnonymousUser
        request = self.factory.get('/test/path/')
        request.user = AnonymousUser()

        response = self.middleware(request)

        self.assertEqual(RequestLog.objects.count(), 1)

        log = RequestLog.objects.first()
        self.assertEqual(log.user, None)
        self.assertFalse(log.is_authenticated)

    def test_middleware_excludes_static_paths(self):
        request = self.factory.get('/static/css/style.css')
        request.user = self.user

        response = self.middleware(request)

        self.assertEqual(RequestLog.objects.count(), 0)

    def test_middleware_excludes_excluded_methods(self):
        request = self.factory.options('/test/path/')
        request.user = self.user

        response = self.middleware(request)

        self.assertEqual(RequestLog.objects.count(), 0)

    def test_middleware_logs_response_time(self):
        request = self.factory.get('/test/path/')
        request.user = self.user

        response = self.middleware(request)

        log = RequestLog.objects.first()
        # Response time should be logged (even if small)
        self.assertIsNotNone(log.response_time_ms)
        self.assertGreaterEqual(log.response_time_ms, 0)

    def test_middleware_logs_client_ip(self):
        request = self.factory.get('/test/path/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        response = self.middleware(request)

        log = RequestLog.objects.first()
        self.assertEqual(log.remote_ip, '192.168.1.100')

    def test_middleware_logs_x_forwarded_for(self):
        request = self.factory.get('/test/path/')
        request.user = self.user
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.195, 70.41.3.18, 150.172.238.178'

        response = self.middleware(request)

        log = RequestLog.objects.first()
        self.assertEqual(log.remote_ip, '203.0.113.195')

    def test_middleware_logs_user_agent(self):
        request = self.factory.get('/test/path/')
        request.user = self.user
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        response = self.middleware(request)

        log = RequestLog.objects.first()
        self.assertIn('Mozilla', log.user_agent)

    def test_middleware_logs_query_string(self):
        request = self.factory.get('/test/path/?param1=value1&param2=value2')
        request.user = self.user

        response = self.middleware(request)

        log = RequestLog.objects.first()
        self.assertEqual(log.query_string, 'param1=value1&param2=value2')

    def test_middleware_handles_exception_gracefully(self):
        request = self.factory.get('/test/path/')
        request.user = self.user

        with patch('audit.models.RequestLog.objects.create', side_effect=Exception("Database error")):
            response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestLog.objects.count(), 0)

    def test_middleware_logs_staff_user_properties(self):
        staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )

        request = self.factory.get('/test/path/')
        request.user = staff_user

        response = self.middleware(request)

        log = RequestLog.objects.first()
        self.assertTrue(log.is_staff)
        self.assertTrue(log.is_superuser)

    def test_middleware_logs_different_status_codes(self):
        request = self.factory.get('/test/path/')
        request.user = self.user

        # Create a custom response with 404 status
        from django.http import HttpResponse
        def mock_404_response(request):
            response = HttpResponse("Not Found")
            response.status_code = 404
            return response

        middleware = RequestLoggingMiddleware(mock_404_response)
        response = middleware(request)

        log = RequestLog.objects.first()
        self.assertEqual(log.response_status, 404)
        self.assertTrue(log.is_client_error)