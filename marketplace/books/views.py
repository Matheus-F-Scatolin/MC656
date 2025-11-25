from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import json

from .models import Book
from .search_strategies import BookSearchService
from .utils import validate_isbn
from bookshelves.models import Bookshelf, BookshelfItem

from donations.models import DonationListing


@login_required
def book_list(request):
    """View to display all available books."""
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})


@login_required
def search_books(request):
    """View to search for books using strategy-based logic."""
    mode = request.GET.get("mode", "combined")
    search_service = BookSearchService(strategy_name=mode)
    books = search_service.search(request)
    listings =  DonationListing.objects.filter(book__in=books, status='A').exclude(donor=request.user)

    context = {
        "books": books,
        "listings": listings,
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
        isbn = request.POST.get('isbn', '').strip()

        if not (title and author and course):
            error_message = "Title, author, and course are required."
            return render(request, 'books/register_book.html', {'error': error_message})
        
        # Validate ISBN if provided
        if isbn and not validate_isbn(isbn):
            error_message = "Invalid ISBN format. Please provide a valid ISBN-10 or ISBN-13."
            return render(request, 'books/register_book.html', {
                'error': error_message,
                'title': title,
                'author': author,
                'course': course,
                'isbn': isbn
            })
        
        try:
            book = Book.objects.create(
                title=title,
                author=author,
                course=course,
                isbn=isbn if isbn else None
            )
            return redirect('book_list')
        except ValidationError as e:
            error_message = str(e)
            return render(request, 'books/register_book.html', {
                'error': error_message,
                'title': title,
                'author': author,
                'course': course,
                'isbn': isbn
            })
        except Exception as e:
            error_message = f"Error creating book: {str(e)}"
            return render(request, 'books/register_book.html', {
                'error': error_message,
                'title': title,
                'author': author,
                'course': course,
                'isbn': isbn
            })

    return render(request, 'books/register_book.html')


@login_required
def add_to_shelf(request, book_id):
    """View to add a book to user's bookshelf with a specific tag."""
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        tag = request.POST.get('tag', 0)

        try:
            # Get or create user's bookshelf
            bookshelf, created = Bookshelf.get_or_create_for_user(request.user)
            
            # Add or update the book in the shelf
            bookshelf_item, item_created = bookshelf.add_or_update_item(
                book=book, 
                tag=tag, 
                actor=request.user
            )
            
            return redirect('book_list')
            
        except ValueError as e:
            # Handle invalid tag values or other validation errors
            # In a production app, you might want to show an error message to the user
            # For now, we'll just redirect back to the book list
            return redirect('book_list')


    return redirect('book_list')


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
            'isbn': book.isbn,
            'created_at': book.created_at.isoformat(),
            'updated_at': book.updated_at.isoformat(),
        })
    return JsonResponse({'books': book_data})


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
            "isbn": b.isbn,
            "created_at": b.created_at.isoformat(),
        }
        for b in books
    ]

    return JsonResponse({
        "books": book_data,
        "count": len(book_data),
        "mode": mode,
    })


@csrf_exempt
@require_POST
@login_required
def register_book_api(request):
    """API endpoint to register a new book (POST)."""
    try:
        data = json.loads(request.body)
        
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        course = data.get('course', '').strip()
        isbn = data.get('isbn', '').strip()
        
        # Validate required fields
        if not (title and author and course):
            return JsonResponse({
                'error': 'Title, author, and course are required fields.'
            }, status=400)
        
        # Validate ISBN if provided
        if isbn and not validate_isbn(isbn):
            return JsonResponse({
                'error': 'Invalid ISBN format. Please provide a valid ISBN-10 or ISBN-13.'
            }, status=400)
        
        # Create the book
        try:
            book = Book.objects.create(
                title=title,
                author=author,
                course=course,
                isbn=isbn if isbn else None
            )
            
            return JsonResponse({
                'success': True,
                'book': {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'course': book.course,
                    'isbn': book.isbn,
                    'created_at': book.created_at.isoformat(),
                    'updated_at': book.updated_at.isoformat(),
                }
            }, status=201)
            
        except ValidationError as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
        except Exception as e:
            # Handle duplicate ISBN or other database errors
            error_msg = str(e)
            if 'UNIQUE constraint failed' in error_msg or 'duplicate' in error_msg.lower():
                return JsonResponse({
                    'error': 'A book with this ISBN already exists.'
                }, status=400)
            return JsonResponse({
                'error': f'Error creating book: {error_msg}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format in request body.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Unexpected error: {str(e)}'
        }, status=500)
