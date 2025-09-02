from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing_page(request):
    """Landing page that redirects based on authentication status."""
    if request.user.is_authenticated:
        return redirect('book_list')
    return render(request, 'accounts/landing.html')
