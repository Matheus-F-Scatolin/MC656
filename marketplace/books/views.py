from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Book
import json

# Create your views here.

def book_list(request):
    """View to display all available books."""
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

def register_book(request):
    """View to register a new book."""
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        course = request.POST.get('course')
        
        if title and author and course:
            book = Book.objects.create(
                title=title,
                author=author,
                course=course
            )
            return redirect('book_list')
        else:
            error_message = "All fields are required."
            return render(request, 'books/register_book.html', {'error': error_message})
    
    return render(request, 'books/register_book.html')

@csrf_exempt
@require_http_methods(["GET"])
def book_list_api(request):
    """API endpoint to return all books as JSON."""
    books = Book.objects.all()
    book_data = []
    for book in books:
        book_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'course': book.course,
            'created_at': book.created_at.isoformat(),
            'updated_at': book.updated_at.isoformat(),
        })
    return JsonResponse({'books': book_data})

def search_books(request):
    """View to search for books by title, author, or course."""
    query = request.GET.get('q', '').strip()
    books = []
    
    if query:
        # Search in title, author, or course fields (case-insensitive)
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(course__icontains=query)
        ).distinct()
    
    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'books/search_books.html', context)

@csrf_exempt
@require_http_methods(["GET"])
def search_books_api(request):
    """API endpoint to search for books and return results as JSON."""
    query = request.GET.get('q', '').strip()
    books = []
    
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(course__icontains=query)
        ).distinct()
    
    book_data = []
    for book in books:
        book_data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'course': book.course,
            'created_at': book.created_at.isoformat(),
            'updated_at': book.updated_at.isoformat(),
        })
    
    return JsonResponse({
        'books': book_data,
        'query': query,
        'count': len(book_data)
    })
