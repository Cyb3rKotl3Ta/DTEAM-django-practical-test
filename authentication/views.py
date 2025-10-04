from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from .forms import CustomUserCreationForm, EmailAuthenticationForm


@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:cv_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Try to find user by email
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    next_url = request.GET.get('next', 'main:cv_list')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})


@login_required
def profile_view(request):
    return JsonResponse({
        'user': {
            'username': request.user.username,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'date_joined': request.user.date_joined.isoformat(),
            'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
        },
        'permissions': list(request.user.get_all_permissions()),
        'groups': list(request.user.groups.values_list('name', flat=True)),
    })


def logout_view(request):
    """Logout view with proper redirect."""
    logout(request)
    return redirect('main:cv_list')


def auth_status_view(request):
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
        'is_staff': request.user.is_staff if request.user.is_authenticated else False,
        'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
    })


@csrf_exempt
def test_login_view(request):
    """Test login endpoint without CSRF for debugging."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'status': 'success',
                    'message': f'Logged in as {username}',
                    'authenticated': True,
                    'username': username
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials',
                    'authenticated': False
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Username and password required',
                'authenticated': False
            })

    return JsonResponse({
        'status': 'error',
        'message': 'POST method required',
        'authenticated': False
    })
