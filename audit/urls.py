from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_home_view, name='audit_home'),
    path('logs/', views.RecentRequestsView.as_view(), name='recent_requests'),
    path('api-logs/', views.api_logs_page_view, name='api_logs_page'),
    path('statistics/', views.statistics_page_view, name='statistics_page'),
    path('api/logs/', views.logs_api_view, name='logs_api'),
    path('api/logs/<int:log_id>/', views.log_detail_view, name='log_detail'),
    path('api/stats/', views.logs_stats_view, name='logs_stats'),
]
