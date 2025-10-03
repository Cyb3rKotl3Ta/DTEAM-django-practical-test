from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import RequestLog


class RecentRequestsView(LoginRequiredMixin, ListView):
    model = RequestLog
    template_name = 'audit/recent_requests.html'
    context_object_name = 'request_logs'
    paginate_by = 20
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = RequestLog.objects.select_related('user').all()

        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(path__icontains=search_query) |
                Q(http_method__icontains=search_query) |
                Q(remote_ip__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )

        # Filter by HTTP method
        method_filter = self.request.GET.get('method')
        if method_filter:
            queryset = queryset.filter(http_method=method_filter)

        # Filter by status code
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(response_status=status_filter)

        # Filter by authentication status
        auth_filter = self.request.GET.get('auth')
        if auth_filter == 'authenticated':
            queryset = queryset.filter(is_authenticated=True)
        elif auth_filter == 'anonymous':
            queryset = queryset.filter(is_authenticated=False)

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add statistics
        context['stats'] = RequestLog.objects.get_stats()
        context['total_logs'] = RequestLog.objects.count()

        # Add filter options
        context['http_methods'] = RequestLog.objects.values_list('http_method', flat=True).distinct().order_by('http_method')
        context['status_codes'] = RequestLog.objects.values_list('response_status', flat=True).distinct().order_by('response_status')

        # Add current filters
        context['current_search'] = self.request.GET.get('search', '')
        context['current_method'] = self.request.GET.get('method', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_auth'] = self.request.GET.get('auth', '')

        return context


@require_http_methods(["GET"])
@cache_page(60 * 5)  # Cache for 5 minutes
def logs_api_view(request):
    """
    API endpoint for recent requests data
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    limit = min(int(request.GET.get('limit', 10)), 100)  # Max 100 records
    offset = int(request.GET.get('offset', 0))

    queryset = RequestLog.objects.select_related('user').all().order_by('-timestamp')

    # Apply filters
    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(path__icontains=search_query) |
            Q(http_method__icontains=search_query) |
            Q(remote_ip__icontains=search_query)
        )

    method_filter = request.GET.get('method')
    if method_filter:
        queryset = queryset.filter(http_method=method_filter)

    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(response_status=status_filter)

    # Get paginated results
    logs = queryset[offset:offset + limit]

    data = {
        'logs': [
            {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'http_method': log.http_method,
                'path': log.path,
                'query_string': log.query_string,
                'remote_ip': log.remote_ip,
                'user_agent': log.user_agent,
                'user': {
                    'username': log.user.username,
                    'email': log.user.email
                } if log.user else None,
                'response_status': log.response_status,
                'response_time_ms': log.response_time_ms,
                'request_size_bytes': log.request_size_bytes,
                'response_size_bytes': log.response_size_bytes,
                'is_authenticated': log.is_authenticated,
                'is_staff': log.is_staff,
                'is_superuser': log.is_superuser,
                'is_successful': log.is_successful,
                'is_client_error': log.is_client_error,
                'is_server_error': log.is_server_error,
            }
            for log in logs
        ],
        'total_count': queryset.count(),
        'limit': limit,
        'offset': offset,
        'has_more': queryset.count() > offset + limit
    }

    return JsonResponse(data)


@require_http_methods(["GET"])
@cache_page(60 * 10)  # Cache for 10 minutes
def logs_stats_view(request):
    """
    API endpoint for logging statistics
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    stats = RequestLog.objects.get_stats()

    # Add additional statistics
    stats.update({
        'top_paths': list(RequestLog.objects.get_top_paths(limit=10)),
        'top_ips': list(RequestLog.objects.get_top_ips(limit=10)),
        'method_distribution': list(RequestLog.objects.get_method_distribution()),
        'hourly_distribution': list(RequestLog.objects.get_hourly_distribution()),
    })

    return JsonResponse(stats)