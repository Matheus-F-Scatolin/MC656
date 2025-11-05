from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from books.models import Book
from .models import Bookshelf, BookshelfItem
import json

class BookshelfViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass123')
        self.book = Book.objects.create(title='Test Book', author='Author', course='Course')
        self.bookshelf = Bookshelf.objects.create(user=self.user)
        self.item = BookshelfItem.objects.create(book=self.book, bookshelf=self.bookshelf, tag=0)

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
        payload = {'id': self.item.id, 'tag': 2}
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.tag, 2)
        self.assertJSONEqual(response.content, {'success': True})

    def test_update_tag_invalid_item(self):
        """Should return 404 when item does not exist."""
        self.client.login(username='tester', password='pass123')
        url = reverse('bookshelves:update_tag')
        payload = {'id': 999, 'tag': 3}
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
            data=json.dumps({'id': self.item.id, 'tag': 1}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)


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
            tag=1, 
            actor=self.user
        )
        
        self.assertTrue(created)
        self.assertEqual(item.book, self.book1)
        self.assertEqual(item.bookshelf, self.bookshelf)
        self.assertEqual(item.tag, 1)
        
        # Verify the item exists in database
        db_item = BookshelfItem.objects.get(book=self.book1, bookshelf=self.bookshelf)
        self.assertEqual(db_item.tag, 1)
    
    def test_add_or_update_item_existing_book(self):
        """Test updating an existing book's tag in the shelf."""
        # First add the book
        BookshelfItem.objects.create(
            book=self.book1, 
            bookshelf=self.bookshelf, 
            tag=0
        )
        
        # Update the tag
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=2, 
            actor=self.user
        )
        
        self.assertFalse(created)
        self.assertEqual(item.tag, 2)
        
        # Verify only one item exists and it has the new tag
        items = BookshelfItem.objects.filter(book=self.book1, bookshelf=self.bookshelf)
        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().tag, 2)
    
    def test_add_or_update_item_string_tag(self):
        """Test that string tags are converted to integers."""
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag="3", 
            actor=self.user
        )
        
        self.assertTrue(created)
        self.assertEqual(item.tag, 3)
        self.assertIsInstance(item.tag, int)
    
    def test_add_or_update_item_none_book_raises_error(self):
        """Test that passing None as book raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.bookshelf.add_or_update_item(
                book=None, 
                tag=1, 
                actor=self.user
            )
        
        self.assertIn("Book cannot be None", str(context.exception))
    
    def test_add_or_update_item_invalid_tag_raises_error(self):
        """Test that invalid tag values raise ValueError."""
        invalid_tags = ['invalid', None, [], {}]
        
        for invalid_tag in invalid_tags:
            with self.assertRaises(ValueError) as context:
                self.bookshelf.add_or_update_item(
                    book=self.book1, 
                    tag=invalid_tag, 
                    actor=self.user
                )
            
            self.assertIn("Tag must be a valid integer", str(context.exception))
    
    def test_add_or_update_item_without_actor(self):
        """Test that actor parameter is optional."""
        item, created = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=1
        )
        
        self.assertTrue(created)
        self.assertEqual(item.book, self.book1)
        self.assertEqual(item.tag, 1)
    
    def test_add_or_update_item_multiple_books(self):
        """Test adding multiple different books to the shelf."""
        # Add first book
        item1, created1 = self.bookshelf.add_or_update_item(
            book=self.book1, 
            tag=1
        )
        
        # Add second book
        item2, created2 = self.bookshelf.add_or_update_item(
            book=self.book2, 
            tag=2
        )
        
        self.assertTrue(created1)
        self.assertTrue(created2)
        self.assertEqual(item1.book, self.book1)
        self.assertEqual(item2.book, self.book2)
        self.assertEqual(item1.tag, 1)
        self.assertEqual(item2.tag, 2)
        
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
            {'tag': '1'}
        )
        
        # Should redirect to book_list
        self.assertRedirects(response, reverse('book_list'))
        
        # Verify bookshelf and item were created
        bookshelf = Bookshelf.objects.get(user=self.user)
        item = BookshelfItem.objects.get(book=self.book, bookshelf=bookshelf)
        self.assertEqual(item.tag, 1)
    
    def test_add_to_shelf_updates_existing_item(self):
        """Test that add_to_shelf updates tag of existing bookshelf item."""
        self.client.login(username='testuser', password='pass123')
        
        # Create existing bookshelf and item
        bookshelf = Bookshelf.objects.create(user=self.user)
        existing_item = BookshelfItem.objects.create(
            book=self.book, 
            bookshelf=bookshelf, 
            tag=0
        )
        
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': '3'}
        )
        
        # Should redirect to book_list
        self.assertRedirects(response, reverse('book_list'))
        
        # Verify tag was updated
        existing_item.refresh_from_db()
        self.assertEqual(existing_item.tag, 3)
        
        # Verify only one item exists
        items = BookshelfItem.objects.filter(book=self.book, bookshelf=bookshelf)
        self.assertEqual(items.count(), 1)
    
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
            {'tag': '1'}
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_add_to_shelf_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.post(
            reverse('add_to_shelf', kwargs={'book_id': self.book.id}),
            {'tag': '1'}
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
