from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from books.models import Book
from .models import Bookshelf, BookshelfItem, BookshelfTag
import json


class BookshelfViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass123')
        self.book = Book.objects.create(title='Test Book', author='Author', course='Course')
        self.bookshelf = Bookshelf.objects.create(user=self.user)
        self.item = BookshelfItem.objects.create(book=self.book, bookshelf=self.bookshelf, tag=BookshelfTag.UNTAGGED)

    def test_bookshelf_view_requires_login(self):
        """Anonymous users should be redirected to login."""
        response = self.client.get(reverse('bookshelves:bookshelf'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_bookshelf_view_logged_in(self):
        """Logged-in users should see their bookshelf."""
        self.client.login(username='tester', password='pass123')
        response = self.client.get(reverse('bookshelves:bookshelf'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookshelves/bookshelf.html')
        self.assertContains(response, 'My Bookshelf')

    def test_remove_from_bookshelf_removes_item(self):
        """Should remove an item from the user's bookshelf."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:remove_from_bookshelf', args=[self.book.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BookshelfItem.objects.filter(book=self.book, bookshelf=self.bookshelf).exists())

    def test_update_tag_success(self):
        """Should update the tag of an existing bookshelf item."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:update_tag')
        payload = {'id': self.item.id, 'tag': BookshelfTag.READING}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.tag, BookshelfTag.READING)
        self.assertJSONEqual(response.content, {'success': True})

    def test_update_tag_invalid_item(self):
        """Should return 404 when item does not exist."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:update_tag')
        payload = {'id': 999, 'tag': BookshelfTag.READ}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_update_tag_invalid_method(self):
        """Should return 400 for non-POST requests."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:update_tag')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_update_tag_unauthenticated(self):
        """Anonymous users should be redirected to login."""
        url = reverse('bookshelves:update_tag')
        response = self.client.post(
            url,
            data=json.dumps({'id': self.item.id, 'tag': BookshelfTag.WANTED}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_update_tag_backward_compatibility_integer(self):
        """Should handle integer tag values for backward compatibility."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:update_tag')
        payload = {'id': self.item.id, 'tag': 2}  # Integer value
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.tag, BookshelfTag.READING)  # Should be stored as string
        self.assertJSONEqual(response.content, {'success': True})

    def test_update_tag_invalid_value(self):
        """Should return error for invalid tag values."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:update_tag')
        payload = {'id': self.item.id, 'tag': '99'}  # Invalid tag value
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_bookshelf_tag_choices(self):
        """Test that BookshelfTag choices are correctly defined."""
        expected_choices = [
            ('0', 'Untagged'),
            ('1', 'Wanted'),
            ('2', 'Reading'),
            ('3', 'Read'),
        ]
        self.assertEqual(BookshelfTag.choices, expected_choices)

    def test_bookshelf_view_provides_tag_choices(self):
        """Test that bookshelf view provides tag choices to template."""
        self.client.login(username='tester', password='pass123')
        response = self.client.get(reverse('bookshelves:bookshelf'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('tag_choices', response.context)
        self.assertIn('tag_choices_json', response.context)
        self.assertEqual(response.context['tag_choices'], BookshelfTag.choices)

    def test_item_get_tag_display(self):
        """Test that BookshelfItem.get_tag_display() works correctly."""
        # Test default untagged
        self.assertEqual(self.item.get_tag_display(), 'Untagged')
        
        # Test other tags
        self.item.tag = BookshelfTag.WANTED
        self.assertEqual(self.item.get_tag_display(), 'Wanted')
        
        self.item.tag = BookshelfTag.READING
        self.assertEqual(self.item.get_tag_display(), 'Reading')
        
        self.item.tag = BookshelfTag.READ
        self.assertEqual(self.item.get_tag_display(), 'Read')
