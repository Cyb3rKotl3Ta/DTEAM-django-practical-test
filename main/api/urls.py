from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cvs', views.CVViewSet, basename='cv')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'api', views.APIHomeView, basename='api-home')

urlpatterns = [
    path('', include(router.urls)),
]
