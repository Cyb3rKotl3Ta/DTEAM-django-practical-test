from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch, Count
<<<<<<< Updated upstream
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
=======
>>>>>>> Stashed changes
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import CV, Skill, Project, Contact
from .services.pdf_service import PDFService
<<<<<<< Updated upstream
from .forms import SendCVEmailForm
from .tasks import send_cv_pdf_email
=======
from .services.translation_service import get_translation_service
from .utils.cv_data_utils import prepare_cv_data
from .forms import SendCVEmailForm
from .tasks import send_cv_pdf_email
from .constants.languages import LANGUAGE_NAMES
>>>>>>> Stashed changes


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

    language = request.GET.get('language')
    pdf_service = PDFService()
    return pdf_service.generate_cv_pdf(cv, language)


def cv_pdf_view_view(request, cv_id):
    cv = get_object_or_404(
        CV.objects.published().select_related().prefetch_related(
            Prefetch('skills', queryset=Skill.objects.select_related()),
            Prefetch('projects', queryset=Project.objects.select_related()),
            Prefetch('contacts', queryset=Contact.objects.filter(is_public=True))
        ),
        id=cv_id
    )

    language = request.GET.get('language')
    pdf_service = PDFService()
    return pdf_service.generate_cv_pdf_inline(cv, language)


<<<<<<< Updated upstream
class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'main/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Django Settings',
            'settings_categories': self._get_settings_categories(),
            'environment_info': self._get_environment_info(),
        })
        return context

    def _get_settings_categories(self):
=======
@login_required
def settings_view(request):
    def get_settings_categories():
>>>>>>> Stashed changes
        return {
            'Core Django': [
                'DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS', 'TIME_ZONE',
                'LANGUAGE_CODE', 'USE_I18N', 'USE_TZ'
            ],
            'Database': [
                'DATABASES'
            ],
            'Static & Media': [
                'STATIC_URL', 'MEDIA_URL', 'STATIC_ROOT', 'MEDIA_ROOT'
            ],
            'Security': [
                'SECURE_SSL_REDIRECT', 'SECURE_HSTS_SECONDS', 'SECURE_HSTS_INCLUDE_SUBDOMAINS',
                'SECURE_HSTS_PRELOAD', 'SECURE_CONTENT_TYPE_NOSNIFF', 'SECURE_BROWSER_XSS_FILTER',
                'X_FRAME_OPTIONS', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE'
            ],
            'Session & CSRF': [
                'SESSION_ENGINE', 'SESSION_COOKIE_AGE', 'SESSION_COOKIE_SECURE',
                'SESSION_COOKIE_HTTPONLY', 'SESSION_COOKIE_SAMESITE', 'CSRF_COOKIE_HTTPONLY',
                'CSRF_COOKIE_SAMESITE'
            ],
            'Email': [
                'EMAIL_BACKEND', 'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USE_TLS', 'EMAIL_USE_SSL'
            ],
            'File Upload': [
                'FILE_UPLOAD_MAX_MEMORY_SIZE', 'DATA_UPLOAD_MAX_MEMORY_SIZE', 'DATA_UPLOAD_MAX_NUMBER_FIELDS'
            ],
            'Custom Project': [
                'DJANGO_ENV', 'REQUEST_LOG_EXCLUDED_PATHS', 'REQUEST_LOG_EXCLUDED_METHODS',
                'REQUEST_LOG_AUTHENTICATED_ONLY'
            ],
            'System Info': [
                'PYTHON_VERSION', 'DJANGO_VERSION', 'CURRENT_TIME', 'SERVER_NAME',
                'SERVER_PORT', 'HTTP_HOST', 'REQUEST_METHOD', 'PATH_INFO',
                'QUERY_STRING', 'REMOTE_ADDR', 'HTTP_USER_AGENT'
            ]
        }

<<<<<<< Updated upstream
    def _get_environment_info(self):
        return {
            'user': self.request.user,
            'is_staff': self.request.user.is_staff,
            'is_superuser': self.request.user.is_superuser,
            'user_permissions': list(self.request.user.get_all_permissions()),
            'user_groups': list(self.request.user.groups.values_list('name', flat=True)),
        }
=======
    def get_environment_info():
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return {
                'user': user,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'user_permissions': list(user.get_all_permissions()),
                'user_groups': list(user.groups.values_list('name', flat=True)),
            }
        else:
            return {
                'user': None,
                'is_staff': False,
                'is_superuser': False,
                'user_permissions': [],
                'user_groups': [],
            }

    context = {
        'page_title': 'Django Settings',
        'settings_categories': get_settings_categories(),
        'environment_info': get_environment_info(),
    }

    return render(request, 'main/settings.html', context)
>>>>>>> Stashed changes


@require_POST
def send_cv_email_view(request, cv_id):
    cv = get_object_or_404(CV.objects.published(), id=cv_id)
    form = SendCVEmailForm(request.POST)

    if form.is_valid():
        recipient_email = form.cleaned_data['recipient_email']
        sender_name = form.cleaned_data.get('sender_name', '')

        task = send_cv_pdf_email.delay(cv_id, recipient_email, sender_name)

        return JsonResponse({
            'status': 'success',
            'task_id': task.id
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid form data',
            'errors': form.errors
        }, status=400)
<<<<<<< Updated upstream
=======


@require_POST
def translate_cv_view(request, cv_id):
    cv = get_object_or_404(CV.objects.published(), id=cv_id)
    target_language = request.POST.get('language')

    if not target_language or target_language not in LANGUAGE_NAMES:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid language selection'
        }, status=400)

    try:
        cv_data = prepare_cv_data(cv)

        translation_service = get_translation_service()
        translated_data = translation_service.translate_cv_content(cv_data, target_language)

        return JsonResponse({
            'status': 'success',
            'message': f'CV translated to {LANGUAGE_NAMES[target_language]}',
            'translated_data': translated_data,
            'language': target_language,
            'language_name': LANGUAGE_NAMES[target_language]
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Translation failed: {str(e)}'
        }, status=500)
>>>>>>> Stashed changes
