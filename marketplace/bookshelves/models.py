from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class Bookshelf(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through='BookshelfItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s shelf"
    
    def add_or_update_item(self, book, tag, actor=None):
        """
        Add a book to the shelf or update its tag if it already exists.
        
        Args:
            book: The Book instance to add/update
            tag: The tag value to assign to the book
            actor: The user performing this action (optional, for future logging/permissions)
            
        Returns:
            tuple: (BookshelfItem instance, boolean created)
            
        Raises:
            ValueError: If book is None or tag is not a valid integer
        """
        if book is None:
            raise ValueError("Book cannot be None")
        
        try:
            tag = int(tag)
        except (ValueError, TypeError):
            raise ValueError("Tag must be a valid integer")
            
        # Create or update the BookshelfItem
        bookshelf_item, created = BookshelfItem.objects.get_or_create(
            book=book,
            bookshelf=self,
            defaults={'tag': tag}
        )
        
        # Update tag if entry already exists
        if not created:
            bookshelf_item.tag = tag
            bookshelf_item.save()
            
        return bookshelf_item, created
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Get or create a bookshelf for the given user.
        
        Args:
            user: The User instance to get/create bookshelf for
            
        Returns:
            tuple: (Bookshelf instance, boolean created)
        """
        return cls.objects.get_or_create(user=user)

class BookshelfItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    bookshelf = models.ForeignKey(Bookshelf, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    tag = models.IntegerField(default=0)

    class Meta:
        unique_together = ['book', 'bookshelf']