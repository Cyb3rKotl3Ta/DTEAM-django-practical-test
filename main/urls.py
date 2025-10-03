from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.cv_list_view, name='cv_list'),
    path('api/', views.home_view, name='api_home'),
]
