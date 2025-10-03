"""
Settings package for CVProject.

This package contains environment-specific settings following Django best practices.
"""

import os
from .base import *

# Determine which settings to use based on environment
ENVIRONMENT = os.environ.get('DJANGO_SETTINGS_MODULE', 'CVProject.settings.development')

if 'production' in ENVIRONMENT:
    from .production import *
elif 'testing' in ENVIRONMENT:
    from .testing import *
else:
    from .development import *
