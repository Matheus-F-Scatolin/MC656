from django.db import models
from django.contrib.auth.models import User

from books.models import Book


class BookshelfTag(models.TextChoices):
    UNTAGGED = '0', 'Untagged'
    WANTED = '1', 'Wanted'
    READING = '2', 'Reading'
    READ = '3', 'Read'


class Bookshelf(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through='BookshelfItem')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s shelf"

class BookshelfItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    bookshelf = models.ForeignKey(Bookshelf, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(
        max_length=1,
        choices=BookshelfTag.choices,
        default=BookshelfTag.UNTAGGED
    )

    class Meta:
        unique_together = ['book', 'bookshelf']