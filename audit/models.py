from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator
from .managers import RequestLogManager


class RequestLog(models.Model):
    HTTP_METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
        ('TRACE', 'TRACE'),
    ]

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    http_method = models.CharField(max_length=10, choices=HTTP_METHOD_CHOICES, db_index=True)
    path = models.CharField(max_length=500, validators=[MinLengthValidator(1)])
    query_string = models.TextField(blank=True, null=True)
    remote_ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True
    )
    response_status = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    request_size_bytes = models.PositiveIntegerField(null=True, blank=True)
    response_size_bytes = models.PositiveIntegerField(null=True, blank=True)
    is_authenticated = models.BooleanField(default=False, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    is_superuser = models.BooleanField(default=False, db_index=True)

    objects = RequestLogManager()

    class Meta:
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'http_method']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['remote_ip', 'timestamp']),
            models.Index(fields=['response_status', 'timestamp']),
            models.Index(fields=['path', 'timestamp']),
        ]

    def __str__(self):
        user_info = f" ({self.user.username})" if self.user else ""
        status_info = f" [{self.response_status}]" if self.response_status else ""
        return f"{self.http_method} {self.path}{user_info}{status_info} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @property
    def is_successful(self):
        return self.response_status and 200 <= self.response_status < 300

    @property
    def is_client_error(self):
        return self.response_status and 400 <= self.response_status < 500

    @property
    def is_server_error(self):
        return self.response_status and 500 <= self.response_status < 600

    @property
    def duration_seconds(self):
        return self.response_time_ms / 1000.0 if self.response_time_ms else None

    def get_user_info(self):
        if not self.user:
            return "Anonymous"

        info = self.user.username
        if self.user.email:
            info += f" ({self.user.email})"
        return info