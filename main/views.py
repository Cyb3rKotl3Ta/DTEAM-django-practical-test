from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch, Count
from .models import CV, Skill, Project, Contact


def home_view(request):
    return JsonResponse({
        'message': 'CVProject is working!',
        'status': 'success',
        'version': '1.0.0'
    })


def cv_list_view(request):
    cvs = CV.objects.published().select_related().prefetch_related(
        Prefetch('skills', queryset=Skill.objects.select_related()),
        Prefetch('projects', queryset=Project.objects.select_related()),
        Prefetch('contacts', queryset=Contact.objects.filter(is_public=True))
    ).annotate(
        skills_count=Count('skills'),
        projects_count=Count('projects')
    ).order_by('-created_at')
    
    context = {
        'cvs': cvs,
        'total_cvs': cvs.count()
    }
    return render(request, 'main/cv_list.html', context)
