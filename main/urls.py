"""
URL configuration for main app.

Following DRY principle by centralizing URL patterns.
"""

from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home_view, name='home'),
]
