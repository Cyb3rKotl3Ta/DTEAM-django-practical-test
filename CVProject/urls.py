"""
URL configuration for CVProject project.

Following DRY principle by centralizing URL patterns and using include().
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def redirect_to_audit_logs(request):
    return redirect('/audit/logs/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('audit/', include('audit.urls')),
    path('auth/', include('authentication.urls')),
    path('logs/', redirect_to_audit_logs, name='logs_redirect'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
