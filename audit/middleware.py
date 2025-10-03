import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import RequestLog

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = getattr(settings, 'REQUEST_LOG_EXCLUDED_PATHS', [
            '/admin/jsi18n/',
            '/static/',
            '/media/',
            '/favicon.ico',
        ])
        self.excluded_methods = getattr(settings, 'REQUEST_LOG_EXCLUDED_METHODS', ['OPTIONS'])
        self.log_authenticated_only = getattr(settings, 'REQUEST_LOG_AUTHENTICATED_ONLY', False)
        super().__init__(get_response)

    def process_request(self, request):
        request._start_time = time.time()
        request._request_size = self._get_request_size(request)
        return None

    def process_response(self, request, response):
        if self._should_log_request(request):
            try:
                self._log_request(request, response)
            except Exception as e:
                logger.error(f"Failed to log request: {e}")

        return response

    def _should_log_request(self, request):
        if self.log_authenticated_only and not request.user.is_authenticated:
            return False

        if request.method in self.excluded_methods:
            return False

        for excluded_path in self.excluded_paths:
            if request.path.startswith(excluded_path):
                return False

        return True

    def _log_request(self, request, response):
        start_time = getattr(request, '_start_time', None)
        response_time_ms = None

        if start_time:
            response_time_ms = int((time.time() - start_time) * 1000)

        request_size = getattr(request, '_request_size', None)
        response_size = self._get_response_size(response)

        RequestLog.objects.create(
            http_method=request.method,
            path=request.path[:500],
            query_string=request.META.get('QUERY_STRING', '')[:1000] or None,
            remote_ip=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500] or None,
            user=request.user if request.user.is_authenticated and request.user.pk else None,
            response_status=response.status_code,
            response_time_ms=response_time_ms,
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            is_authenticated=request.user.is_authenticated,
            is_staff=request.user.is_staff if request.user.is_authenticated else False,
            is_superuser=request.user.is_superuser if request.user.is_authenticated else False,
        )

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _get_request_size(self, request):
        try:
            content_length = request.META.get('CONTENT_LENGTH')
            if content_length:
                return int(content_length)

            if hasattr(request, 'body'):
                return len(request.body)

            return None
        except (ValueError, TypeError):
            return None

    def _get_response_size(self, response):
        try:
            if hasattr(response, 'content'):
                return len(response.content)
            return None
        except (ValueError, TypeError):
            return None


class RequestLoggingMiddlewareAsync(RequestLoggingMiddleware):
    async def __call__(self, request):
        request._start_time = time.time()
        request._request_size = self._get_request_size(request)

        response = await self.get_response(request)

        if self._should_log_request(request):
            try:
                self._log_request(request, response)
            except Exception as e:
                logger.error(f"Failed to log request: {e}")

        return response
