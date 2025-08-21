from django.contrib import admin
from .models import Book

# Register your models here.

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'course', 'created_at']
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'author', 'course']
    ordering = ['-created_at']
