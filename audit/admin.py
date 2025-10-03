from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'http_method', 'path_display', 'user_display',
        'response_status_display', 'response_time_display', 'remote_ip'
    ]
    list_filter = [
        'http_method', 'response_status', 'is_authenticated',
        'is_staff', 'is_superuser', 'timestamp'
    ]
    search_fields = ['path', 'remote_ip', 'user__username', 'user__email']
    readonly_fields = [
        'timestamp', 'http_method', 'path', 'query_string', 'remote_ip',
        'user_agent', 'user', 'response_status', 'response_time_ms',
        'request_size_bytes', 'response_size_bytes', 'is_authenticated',
        'is_staff', 'is_superuser', 'user_agent_display'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50

    fieldsets = (
        ('Request Information', {
            'fields': ('timestamp', 'http_method', 'path', 'query_string', 'remote_ip')
        }),
        ('User Information', {
            'fields': ('user', 'is_authenticated', 'is_staff', 'is_superuser')
        }),
        ('Response Information', {
            'fields': ('response_status', 'response_time_ms', 'request_size_bytes', 'response_size_bytes')
        }),
        ('Additional Information', {
            'fields': ('user_agent_display',),
            'classes': ('collapse',)
        }),
    )

    def path_display(self, obj):
        if len(obj.path) > 50:
            return format_html(
                '<span title="{}">{}...</span>',
                obj.path,
                obj.path[:50]
            )
        return obj.path
    path_display.short_description = 'Path'

    def user_display(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.user.username
            )
        return 'Anonymous'
    user_display.short_description = 'User'

    def response_status_display(self, obj):
        if not obj.response_status:
            return '-'

        if obj.is_successful:
            color = 'green'
        elif obj.is_client_error:
            color = 'orange'
        elif obj.is_server_error:
            color = 'red'
        else:
            color = 'black'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.response_status
        )
    response_status_display.short_description = 'Status'

    def response_time_display(self, obj):
        if not obj.response_time_ms:
            return '-'

        if obj.response_time_ms < 100:
            color = 'green'
        elif obj.response_time_ms < 1000:
            color = 'orange'
        else:
            color = 'red'

        return format_html(
            '<span style="color: {};">{}ms</span>',
            color,
            obj.response_time_ms
        )
    response_time_display.short_description = 'Response Time'

    def user_agent_display(self, obj):
        if not obj.user_agent:
            return '-'

        return format_html(
            '<div style="max-width: 400px; word-wrap: break-word; font-family: monospace; font-size: 11px;">{}</div>',
            obj.user_agent
        )
    user_agent_display.short_description = 'User Agent'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')