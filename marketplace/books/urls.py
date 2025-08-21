from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('register/', views.register_book, name='register_book'),
    path('api/books/', views.book_list_api, name='book_list_api'),
]