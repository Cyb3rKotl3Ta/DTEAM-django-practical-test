from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.db.models import Prefetch, Count
from .models import CV, Skill, Project, Contact
from .services.pdf_service import PDFService


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


def cv_detail_view(request, cv_id):
    cv = get_object_or_404(
        CV.objects.published().select_related().prefetch_related(
            Prefetch('skills', queryset=Skill.objects.select_related().order_by('category', 'name')),
            Prefetch('projects', queryset=Project.objects.select_related().order_by('-is_featured', '-start_date')),
            Prefetch('contacts', queryset=Contact.objects.filter(is_public=True).order_by('contact_type'))
        ),
        id=cv_id
    )

    skills_by_category = {}
    for skill in cv.skills.all():
        category = skill.get_category_display()
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)

    featured_projects = cv.projects.filter(is_featured=True)
    other_projects = cv.projects.filter(is_featured=False)

    context = {
        'cv': cv,
        'skills_by_category': skills_by_category,
        'featured_projects': featured_projects,
        'other_projects': other_projects,
        'total_skills': cv.skills.count(),
        'total_projects': cv.projects.count(),
        'total_contacts': cv.contacts.filter(is_public=True).count()
    }
    return render(request, 'main/cv_detail.html', context)


def cv_pdf_download_view(request, cv_id):
    cv = get_object_or_404(
        CV.objects.published().select_related().prefetch_related(
            Prefetch('skills', queryset=Skill.objects.select_related()),
            Prefetch('projects', queryset=Project.objects.select_related()),
            Prefetch('contacts', queryset=Contact.objects.filter(is_public=True))
        ),
        id=cv_id
    )

    pdf_service = PDFService()
    return pdf_service.generate_cv_pdf(cv)


def cv_pdf_view_view(request, cv_id):
    cv = get_object_or_404(
        CV.objects.published().select_related().prefetch_related(
            Prefetch('skills', queryset=Skill.objects.select_related()),
            Prefetch('projects', queryset=Project.objects.select_related()),
            Prefetch('contacts', queryset=Contact.objects.filter(is_public=True))
        ),
        id=cv_id
    )

    pdf_service = PDFService()
    return pdf_service.generate_cv_pdf_inline(cv)
