from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Create your views here.

def landing_page(request):
    """Landing page that serves as the entry point to the application."""
    if request.user.is_authenticated:
        return redirect('book_list')
    return render(request, 'accounts/landing.html')

def signup_view(request):
    """View to handle user registration/signup."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            error_message = "All fields are required."
            return render(request, 'accounts/signup.html', {'error': error_message})
        
        if password != confirm_password:
            error_message = "Passwords do not match."
            return render(request, 'accounts/signup.html', {'error': error_message})
        
        if User.objects.filter(username=username).exists():
            error_message = "Username already exists."
            return render(request, 'accounts/signup.html', {'error': error_message})
        
        if User.objects.filter(email=email).exists():
            error_message = "Email already registered."
            return render(request, 'accounts/signup.html', {'error': error_message})
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')
    
    return render(request, 'accounts/signup.html')

def login_view(request):
    """View to handle user login."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not all([username, password]):
            error_message = "All fields are required."
            return render(request, 'accounts/login.html', {'error': error_message})
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('book_list')
        else:
            error_message = "Invalid username or password."
            return render(request, 'accounts/login.html', {'error': error_message})
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """View to handle user logout."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@csrf_exempt
@require_http_methods(["POST"])
def signup_api(request):
    """API endpoint for user registration."""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)
        
        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match.'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered.'}, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        return JsonResponse({
            'message': 'Account created successfully!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.isoformat()
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred during registration.'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    """API endpoint for user login."""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=200)
        else:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred during login.'}, status=500)
