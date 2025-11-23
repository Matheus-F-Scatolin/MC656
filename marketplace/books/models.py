from django.db import models
from django.core.exceptions import ValidationError
from .utils import validate_isbn, normalize_isbn


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    course = models.CharField(max_length=100, help_text="University course related to this book")
    isbn = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        unique=True,
        help_text="ISBN-10 or ISBN-13 (stored normalized without hyphens/spaces)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def clean(self):
        """Validate the ISBN if provided."""
        super().clean()
        if self.isbn:
            # Validate the ISBN (should already be normalized at this point)
            if not validate_isbn(self.isbn):
                raise ValidationError({
                    'isbn': 'Invalid ISBN format. Please provide a valid ISBN-10 or ISBN-13.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to normalize and validate."""
        # Normalize ISBN BEFORE validation
        if self.isbn:
            self.isbn = normalize_isbn(self.isbn)
        
        # Now validate
        self.full_clean()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
