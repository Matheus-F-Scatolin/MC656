from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('register/', views.register_book, name='register_book'),
    path('search/', views.search_books, name='search_books'),
    path('api/books/', views.book_list_api, name='book_list_api'),
    path('api/search/', views.search_books_api, name='search_books_api'),
]