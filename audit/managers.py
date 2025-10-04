from django.db import models
from django.utils import timezone
from datetime import timedelta


class RequestLogManager(models.Manager):
    def successful(self):
        return self.filter(response_status__gte=200, response_status__lt=300)

    def client_errors(self):
        return self.filter(response_status__gte=400, response_status__lt=500)

    def server_errors(self):
        return self.filter(response_status__gte=500, response_status__lt=600)

    def by_method(self, method):
        return self.filter(http_method=method.upper())

    def by_user(self, user):
        return self.filter(user=user)

    def by_ip(self, ip):
        return self.filter(remote_ip=ip)

    def by_path(self, path):
        return self.filter(path__icontains=path)

    def authenticated_only(self):
        return self.filter(is_authenticated=True)

    def anonymous_only(self):
        return self.filter(is_authenticated=False)

    def staff_only(self):
        return self.filter(is_staff=True)

    def superuser_only(self):
        return self.filter(is_superuser=True)

    def recent(self, hours=24):
        since = timezone.now() - timedelta(hours=hours)
        return self.filter(timestamp__gte=since)

    def today(self):
        today = timezone.now().date()
        return self.filter(timestamp__date=today)

    def this_week(self):
        week_ago = timezone.now() - timedelta(days=7)
        return self.filter(timestamp__gte=week_ago)

    def this_month(self):
        month_ago = timezone.now() - timedelta(days=30)
        return self.filter(timestamp__gte=month_ago)

    def slow_requests(self, threshold_ms=1000):
        return self.filter(response_time_ms__gte=threshold_ms)

    def large_requests(self, threshold_bytes=1024*1024):
        return self.filter(request_size_bytes__gte=threshold_bytes)

    def large_responses(self, threshold_bytes=1024*1024):
        return self.filter(response_size_bytes__gte=threshold_bytes)

    def get_stats(self):
        total = self.count()
        successful = self.successful().count()
        client_errors = self.client_errors().count()
        server_errors = self.server_errors().count()

        return {
            'total_requests': total,
            'successful_requests': successful,
            'client_errors': client_errors,
            'server_errors': server_errors,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'error_rate': ((client_errors + server_errors) / total * 100) if total > 0 else 0,
        }

    def get_top_paths(self, limit=10):
        return self.values('path').annotate(
            count=models.Count('id')
        ).order_by('-count')[:limit]

    def get_top_ips(self, limit=10):
        return self.values('remote_ip').annotate(
            count=models.Count('id')
        ).order_by('-count')[:limit]

    def get_top_users(self, limit=10):
        return self.filter(user__isnull=False).values(
            'user__username', 'user__email'
        ).annotate(
            count=models.Count('id')
        ).order_by('-count')[:limit]

    def get_method_distribution(self):
        return self.values('http_method').annotate(
            count=models.Count('id')
        ).order_by('-count')

    def get_hourly_distribution(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXTRACT(hour FROM timestamp) as hour, COUNT(*) as count
                FROM audit_requestlog
                GROUP BY EXTRACT(hour FROM timestamp)
                ORDER BY hour
            """)
            return [{'hour': str(int(row[0])), 'count': row[1]} for row in cursor.fetchall()]
