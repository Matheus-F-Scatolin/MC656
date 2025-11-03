from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET

from .models import Book
from .search_strategies import BookSearchService


# Create your views here.

@login_required
def book_list(request):
    """View to display all available books."""
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})


@login_required
def search_books_old(request):
    """View to search for books based on query parameters."""
    query = request.GET.get('q', '').strip()
    books = []

    if query:
        # Search in title, author, and course fields
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(course__icontains=query)
        ).distinct()
    else:
        # If no query, show all books
        books = Book.objects.all()

    context = {
        'books': books,
        'query': query,
        'is_search': True
    }
    return render(request, 'books/search_books.html', context)


@login_required
def search_books(request):
    """View to search for books using strategy-based logic."""
    mode = request.GET.get("mode", "combined")
    search_service = BookSearchService(strategy_name=mode)
    books = search_service.search(request)

    context = {
        "books": books,
        "query": request.GET.get("q", "").strip(),
        "mode": mode,
        "is_search": True,
    }
    return render(request, "books/search_books.html", context)


@login_required
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
@login_required
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


@csrf_exempt
@require_GET
@login_required
def search_books_api_old(request):
    """API endpoint using same strategy logic (AJAX)."""
    mode = request.GET.get('mode', 'combined')
    query = request.GET.get('q', '').strip()
    title = request.GET.get('title', '').strip()
    author = request.GET.get('author', '').strip()
    course = request.GET.get('course', '').strip()

    search_service = BookSearchService(strategy_name=mode)

    if mode == 'advanced':
        books = search_service.search(title=title, author=author, course=course)
    else:
        books = search_service.search(query=query)

    data = [{
        'id': b.id,
        'title': b.title,
        'author': b.author,
        'course': b.course,
        'created_at': b.created_at.isoformat(),
    } for b in books]

    return JsonResponse({'books': data, 'count': len(data)})


@csrf_exempt
@require_GET
@login_required
def search_books_api(request):
    """API endpoint for searching books using strategy-based logic."""
    mode = request.GET.get("mode", "combined")
    search_service = BookSearchService(strategy_name=mode)
    books = search_service.search(request)

    book_data = [
        {
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "course": b.course,
            "created_at": b.created_at.isoformat(),
        }
        for b in books
    ]

    return JsonResponse({
        "books": book_data,
        "count": len(book_data),
        "mode": mode,
    })
