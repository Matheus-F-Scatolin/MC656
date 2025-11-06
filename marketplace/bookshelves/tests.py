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


class BookshelfModelTest(TestCase):
    """Test cases for Bookshelf model methods."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.book1 = Book.objects.create(title='Book 1', author='Author 1', course='Course 1')
        self.book2 = Book.objects.create(title='Book 2', author='Author 2', course='Course 2')
        self.bookshelf = Bookshelf.objects.create(user=self.user)
    
    def test_get_or_create_for_user_new_shelf(self):
        """Test creating a new bookshelf for a user."""
        new_user = User.objects.create_user(username='newuser', password='pass123')
        bookshelf, created = Bookshelf.get_or_create_for_user(new_user)
        
        self.assertTrue(created)
        self.assertEqual(bookshelf.user, new_user)
        self.assertIsInstance(bookshelf, Bookshelf)
    
    def test_get_or_create_for_user_existing_shelf(self):
        """Test getting an existing bookshelf for a user."""
        bookshelf, created = Bookshelf.get_or_create_for_user(self.user)
        
        self.assertFalse(created)
        self.assertEqual(bookshelf.user, self.user)
        self.assertEqual(bookshelf, self.bookshelf)
    
    def test_add_or_update_item_new_book(self):
        """Test adding a new book to the shelf."""
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=BookshelfTag.WANTED,  # Use BookshelfTag constant
            actor=self.user
        )
        
        self.assertTrue(created)
        self.assertEqual(item.book, self.book1)
        self.assertEqual(item.bookshelf, self.bookshelf)
        self.assertEqual(item.tag, BookshelfTag.WANTED)  # String value '1'
        
        # Verify the item exists in database
        db_item = BookshelfItem.objects.get(book=self.book1, bookshelf=self.bookshelf)
        self.assertEqual(db_item.tag, BookshelfTag.WANTED)
    
    def test_add_or_update_item_existing_book(self):
        """Test updating an existing book's tag in the shelf."""
        # First add the book
        BookshelfItem.objects.create(
            book=self.book1, 
            bookshelf=self.bookshelf, 
            tag=BookshelfTag.UNTAGGED  # Use BookshelfTag constant
        )
        
        # Update the tag
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=BookshelfTag.READING,  # Use BookshelfTag constant
            actor=self.user
        )
        
        self.assertFalse(created)
        self.assertEqual(item.tag, BookshelfTag.READING)  # String value '2'
        
        # Verify only one item exists and it has the new tag
        items = BookshelfItem.objects.filter(book=self.book1, bookshelf=self.bookshelf)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().tag, BookshelfTag.READING)
    
    def test_add_or_update_item_string_tag(self):
        """Test that string tags are handled correctly."""
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag="3",  # String value (should be valid)
            actor=self.user
        )
        
        self.assertTrue(created)
        self.assertEqual(item.tag, BookshelfTag.READ)  # String value '3'
        self.assertIsInstance(item.tag, str)  # Should be string now, not int
    
    def test_add_or_update_item_backward_compatibility_integer(self):
        """Test that integer tags are converted to strings for backward compatibility."""
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=3,  # Integer value (backward compatibility)
            actor=self.user
        )
        
        self.assertTrue(created)
        self.assertEqual(item.tag, BookshelfTag.READ)  # Should be converted to string '3'
        self.assertIsInstance(item.tag, str)
    
    def test_add_or_update_item_none_book_raises_error(self):
        """Test that passing None as book raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.bookshelf.add_or_update_item(
                book=None, 
                tag=BookshelfTag.WANTED, 
                actor=self.user
            )
        
        self.assertIn("Book cannot be None", str(context.exception))
    
    def test_add_or_update_item_invalid_tag_raises_error(self):
        """Test that invalid tag values raise ValueError."""
        invalid_tags = ['invalid', '99', None, [], {}]
        
        for invalid_tag in invalid_tags:
            with self.assertRaises(ValueError) as context:
                self.bookshelf.add_or_update_item(
                    book=self.book1, 
                    tag=invalid_tag, 
                    actor=self.user
                )
            
            self.assertIn("Tag must be a valid", str(context.exception))
    
    def test_add_or_update_item_without_actor(self):
        """Test that actor parameter is optional."""
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=BookshelfTag.WANTED
        )
        
        self.assertTrue(created)
        self.assertEqual(item.book, self.book1)
        self.assertEqual(item.tag, BookshelfTag.WANTED)
    
    def test_add_or_update_item_multiple_books(self):
        """Test adding multiple different books to the shelf."""
        # Add first book
        item1, created1 = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=BookshelfTag.WANTED
        )
        
        # Add second book
        item2, created2 = self.bookshelf.add_or_update_item(
            book=self.book2, 
            tag=BookshelfTag.READING
        )
        
        self.assertTrue(created1)
        self.assertTrue(created2)
        self.assertEqual(item1.book, self.book1)
        self.assertEqual(item2.book, self.book2)
        self.assertEqual(item1.tag, BookshelfTag.WANTED)
        self.assertEqual(item2.tag, BookshelfTag.READING)
        
        # Verify both items exist
        items = BookshelfItem.objects.filter(bookshelf=self.bookshelf)
        self.assertEqual(items.count(), 2)


class AddToShelfIntegrationTest(TestCase):
    """Integration tests for the add_to_shelf view using the new refactored code."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.book = Book.objects.create(title='Test Book', author='Test Author', course='Test Course')
    
    def test_add_to_shelf_creates_bookshelf_and_item(self):
        """Test that add_to_shelf creates both bookshelf and item for new user."""
        self.client.login(username='testuser', password='pass123')
        
        # Ensure no bookshelf exists initially
        self.assertFalse(Bookshelf.objects.filter(user=self.user).exists())
        
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': BookshelfTag.WANTED}  # Use BookshelfTag constant
        )
        
        # Should redirect to book_list
        self.assertRedirects(response, reverse('book_list'))
        
        # Verify bookshelf and item were created
        bookshelf = Bookshelf.objects.get(user=self.user)
        item = BookshelfItem.objects.get(book=self.book, bookshelf=bookshelf)
        self.assertEqual(item.tag, BookshelfTag.WANTED)
    
    def test_add_to_shelf_updates_existing_item(self):
        """Test that add_to_shelf updates tag of existing bookshelf item."""
        self.client.login(username='testuser', password='pass123')
        
        # Create existing bookshelf and item
        bookshelf = Bookshelf.objects.create(user=self.user)
        existing_item = BookshelfItem.objects.create(
            book=self.book, 
            bookshelf=bookshelf, 
            tag=BookshelfTag.UNTAGGED  # Use BookshelfTag constant
        )
        
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': BookshelfTag.READ}  # Use BookshelfTag constant
        )
        
        # Should redirect to book_list
        self.assertRedirects(response, reverse('book_list'))
        
        # Verify tag was updated
        existing_item.refresh_from_db()
        self.assertEqual(existing_item.tag, BookshelfTag.READ)
        
        # Verify only one item exists
        items = BookshelfItem.objects.filter(book=self.book, bookshelf=bookshelf)
        self.assertEqual(items.count(), 1)
    
    def test_add_to_shelf_backward_compatibility_integer_tag(self):
        """Test that integer tag values still work for backward compatibility."""
        self.client.login(username='testuser', password='pass123')
        
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': '2'}  # String representation of integer
        )
        
        # Should redirect to book_list
        self.assertRedirects(response, reverse('book_list'))
        
        # Verify bookshelf and item were created with correct tag
        bookshelf = Bookshelf.objects.get(user=self.user)
        item = BookshelfItem.objects.get(book=self.book, bookshelf=bookshelf)
        self.assertEqual(item.tag, BookshelfTag.READING)  # '2' should map to READING
    
    def test_add_to_shelf_invalid_tag_handled_gracefully(self):
        """Test that invalid tag values are handled gracefully."""
        self.client.login(username='testuser', password='pass123')
        
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': 'invalid_tag'}
        )
        
        # Should still redirect (graceful error handling)
        self.assertRedirects(response, reverse('book_list'))
        
        # No bookshelf item should be created due to validation error
        self.assertFalse(
            BookshelfItem.objects.filter(book=self.book).exists()
        )
    
    def test_add_to_shelf_nonexistent_book_returns_404(self):
        """Test that requesting nonexistent book returns 404."""
        self.client.login(username='testuser', password='pass123')
        
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': 99999}),
            {'tag': BookshelfTag.WANTED}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_add_to_shelf_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': BookshelfTag.WANTED}
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_add_to_shelf_get_request_redirects(self):
        """Test that GET requests are redirected to book_list."""
        self.client.login(username='testuser', password='pass123')
        
        response = self.client.get(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id})
        )
        
        self.assertRedirects(response, reverse('book_list'))