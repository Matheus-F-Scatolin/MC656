from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Bookshelf, BookshelfItem, BookshelfTag
from books.models import Book


@login_required
def remove_from_bookshelf(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    bookshelf = get_object_or_404(Bookshelf, user=request.user)
    BookshelfItem.objects.filter(book=book, bookshelf=bookshelf).delete()
    return redirect('bookshelves:bookshelf')

@csrf_exempt
@login_required
def update_tag(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('id')
        new_tag = data.get('tag')
        try:
            item = BookshelfItem.objects.get(id=item_id, bookshelf__user=request.user)
            
            # Handle both integer and string values for backward compatibility
            if isinstance(new_tag, int):
                # Convert integer to string for the new CharField
                new_tag = str(new_tag)
            
            # Validate that the tag value is valid
            if new_tag not in [choice[0] for choice in BookshelfTag.choices]:
                return JsonResponse({'error': 'Invalid tag value'}, status=400)
            
            item.tag = new_tag
            item.save()
            return JsonResponse({'success': True})
        except BookshelfItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def bookshelf_view(request):
    bookshelf, created = Bookshelf.objects.get_or_create(user=request.user)
    
    # Provide tag choices to template to eliminate shotgun surgery
    context = {
        'bookshelf': bookshelf,
        'tag_choices': BookshelfTag.choices,
        'tag_choices_json': json.dumps(dict(BookshelfTag.choices))
    }
    
    return render(request, 'bookshelves/bookshelf.html', context)


