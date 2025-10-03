from django.conf import settings
from django.utils import timezone
import os


def settings_context(request):
    """
    Context processor that injects Django settings into all templates.
    
    Following SOLID principles:
    - Single Responsibility: Only handles settings injection
    - Open/Closed: Easy to extend with new settings
    - Dependency Inversion: Uses Django's settings system
    """
    return {
        'settings': {
            # Core Django settings
            'DEBUG': settings.DEBUG,
            'SECRET_KEY': settings.SECRET_KEY[:10] + '...' if settings.SECRET_KEY else None,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'TIME_ZONE': settings.TIME_ZONE,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
            'USE_I18N': settings.USE_I18N,
            'USE_TZ': settings.USE_TZ,
            
            # Database settings
            'DATABASES': {
                'default': {
                    'ENGINE': settings.DATABASES['default']['ENGINE'].split('.')[-1],
                    'NAME': settings.DATABASES['default']['NAME'],
                }
            },
            
            # Static and Media settings
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
            'STATIC_ROOT': settings.STATIC_ROOT,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            
            # Installed apps
            'INSTALLED_APPS': settings.INSTALLED_APPS,
            
            # Middleware
            'MIDDLEWARE': settings.MIDDLEWARE,
            
            # Security settings
            'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
            'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', 0),
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', False),
            'SECURE_HSTS_PRELOAD': getattr(settings, 'SECURE_HSTS_PRELOAD', False),
            'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
            'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False),
            'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', 'DENY'),
            
            # Cache settings
            'CACHES': {
                'default': {
                    'BACKEND': settings.CACHES['default']['BACKEND'].split('.')[-1],
                }
            } if hasattr(settings, 'CACHES') else None,
            
            # Email settings
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend').split('.')[-1],
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'localhost'),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 25),
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', False),
            'EMAIL_USE_SSL': getattr(settings, 'EMAIL_USE_SSL', False),
            
            # Logging settings
            'LOGGING': getattr(settings, 'LOGGING', {}),
            
            # Session settings
            'SESSION_ENGINE': getattr(settings, 'SESSION_ENGINE', 'django.contrib.sessions.backends.db').split('.')[-1],
            'SESSION_COOKIE_AGE': getattr(settings, 'SESSION_COOKIE_AGE', 1209600),
            'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', False),
            'SESSION_COOKIE_HTTPONLY': getattr(settings, 'SESSION_COOKIE_HTTPONLY', True),
            'SESSION_COOKIE_SAMESITE': getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax'),
            
            # CSRF settings
            'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', False),
            'CSRF_COOKIE_HTTPONLY': getattr(settings, 'CSRF_COOKIE_HTTPONLY', False),
            'CSRF_COOKIE_SAMESITE': getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Lax'),
            
            # File upload settings
            'FILE_UPLOAD_MAX_MEMORY_SIZE': getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 2621440),
            'DATA_UPLOAD_MAX_MEMORY_SIZE': getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 2621440),
            'DATA_UPLOAD_MAX_NUMBER_FIELDS': getattr(settings, 'DATA_UPLOAD_MAX_NUMBER_FIELDS', 1000),
            
            # Custom project settings
            'DJANGO_ENV': getattr(settings, 'DJANGO_ENV', 'development'),
            'REQUEST_LOG_EXCLUDED_PATHS': getattr(settings, 'REQUEST_LOG_EXCLUDED_PATHS', []),
            'REQUEST_LOG_EXCLUDED_METHODS': getattr(settings, 'REQUEST_LOG_EXCLUDED_METHODS', []),
            'REQUEST_LOG_AUTHENTICATED_ONLY': getattr(settings, 'REQUEST_LOG_AUTHENTICATED_ONLY', False),
            
            # System information
            'PYTHON_VERSION': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'DJANGO_VERSION': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'CURRENT_TIME': timezone.now(),
            'SERVER_NAME': request.META.get('SERVER_NAME', 'Unknown'),
            'SERVER_PORT': request.META.get('SERVER_PORT', 'Unknown'),
            'HTTP_HOST': request.META.get('HTTP_HOST', 'Unknown'),
            'REQUEST_METHOD': request.META.get('REQUEST_METHOD', 'Unknown'),
            'PATH_INFO': request.META.get('PATH_INFO', 'Unknown'),
            'QUERY_STRING': request.META.get('QUERY_STRING', ''),
            'REMOTE_ADDR': request.META.get('REMOTE_ADDR', 'Unknown'),
            'HTTP_USER_AGENT': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        }
    }
