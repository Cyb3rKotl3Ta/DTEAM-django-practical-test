from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('logs/', views.RecentRequestsView.as_view(), name='recent_requests'),
    path('api/logs/', views.logs_api_view, name='logs_api'),
    path('api/stats/', views.logs_stats_view, name='logs_stats'),
]
