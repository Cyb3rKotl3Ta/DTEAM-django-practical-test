"""
Views for the main app.

Following SOLID principles and DRY approach.
"""

from django.shortcuts import render
from django.http import JsonResponse


def home_view(request):
    """
    Home page view.

    Returns a simple JSON response for testing.
    """
    return JsonResponse({
        'message': 'CVProject is working!',
        'status': 'success',
        'version': '1.0.0'
    })
