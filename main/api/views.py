from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, Count
from django.shortcuts import get_object_or_404

from ..models import CV, Skill, Project, Contact
from ..serializers.cv_serializers import (
    CVListSerializer, CVDetailSerializer, CVCreateUpdateSerializer,
    SkillSerializer, ProjectSerializer, ContactSerializer
)


class CVViewSet(viewsets.ModelViewSet):
    queryset = CV.objects.published().select_related().prefetch_related(
        Prefetch('skills', queryset=Skill.objects.select_related()),
        Prefetch('projects', queryset=Project.objects.select_related()),
        Prefetch('contacts', queryset=Contact.objects.filter(is_public=True))
    ).annotate(
        skills_count=Count('skills'),
        projects_count=Count('projects')
    ).order_by('-created_at')

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active']
    search_fields = ['first_name', 'last_name', 'bio', 'skills__name', 'projects__title']
    ordering_fields = ['created_at', 'updated_at', 'first_name', 'last_name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CVListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CVCreateUpdateSerializer
        return CVDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == 'list':
            return queryset.only(
                'id', 'first_name', 'last_name', 'bio', 'status',
                'is_active', 'created_at', 'updated_at'
            )

        return queryset

    @action(detail=True, methods=['get'])
    def skills(self, request, pk=None):
        cv = self.get_object()
        skills = cv.skills.all().order_by('category', 'name')
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        cv = self.get_object()
        projects = cv.projects.all().order_by('-is_featured', '-start_date')
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def contacts(self, request, pk=None):
        cv = self.get_object()
        contacts = cv.contacts.filter(is_public=True).order_by('contact_type')
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def featured_projects(self, request, pk=None):
        cv = self.get_object()
        featured_projects = cv.projects.filter(is_featured=True).order_by('-start_date')
        serializer = ProjectSerializer(featured_projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def skills_by_category(self, request, pk=None):
        cv = self.get_object()
        skills_by_category = {}

        for skill in cv.skills.all().order_by('category', 'name'):
            category = skill.get_category_display()
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(SkillSerializer(skill).data)

        return Response(skills_by_category)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.select_related('cv').order_by('category', 'name')
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'proficiency_level']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'proficiency_level', 'category']
    ordering = ['category', 'name']


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('cv').order_by('-is_featured', '-start_date')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_featured']
    search_fields = ['title', 'description', 'technologies_used']
    ordering_fields = ['title', 'start_date', 'end_date', 'is_featured']
    ordering = ['-is_featured', '-start_date']


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.select_related('cv').filter(is_public=True).order_by('contact_type')
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact_type', 'is_primary', 'is_public']
    search_fields = ['value']
    ordering_fields = ['contact_type', 'is_primary']
    ordering = ['contact_type']


class APIHomeView(viewsets.ViewSet):
    def list(self, request):
        return Response({
            'message': 'CV Project API',
            'version': '1.0.0',
            'endpoints': {
                'cvs': '/api/cvs/',
                'skills': '/api/skills/',
                'projects': '/api/projects/',
                'contacts': '/api/contacts/',
                'api_root': '/api/',
            },
            'features': [
                'RESTful API endpoints',
                'Pagination support',
                'Search and filtering',
                'Ordering support',
                'Browsable API interface',
                'Authentication support',
            ]
        })
