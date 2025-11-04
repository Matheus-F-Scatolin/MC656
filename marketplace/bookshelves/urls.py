# python (arquivo: `marketplace/bookshelves/urls.py`)
from django.urls import path
from . import views

app_name = 'bookshelves'

urlpatterns = [
    path('bookshelf/', views.bookshelf_view, name='bookshelf'),
    path('bookshelf/remove/<int:book_id>/', views.remove_from_bookshelf, name='remove_from_bookshelf'),
    path('update_tag/', views.update_tag, name='update_tag'),
]
