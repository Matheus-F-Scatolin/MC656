"""
Smoke tests for ISBN functionality.
These are basic tests to ensure the ISBN feature works before comprehensive testing.
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from books.models import Book
from books.utils import validate_isbn, normalize_isbn


class ISBNValidationSmokeTest(TestCase):
    """Smoke tests for ISBN validation utility functions."""
    
    def test_validate_isbn_basic_isbn10(self):
        """Test that a basic valid ISBN-10 is accepted."""
        self.assertTrue(validate_isbn("0596520689"))
    
    def test_validate_isbn_basic_isbn13(self):
        """Test that a basic valid ISBN-13 is accepted."""
        self.assertTrue(validate_isbn("9780596520687"))
    
    def test_validate_isbn_with_hyphens(self):
        """Test that ISBN with hyphens is accepted."""
        self.assertTrue(validate_isbn("978-0-596-52068-7"))
    
    def test_validate_isbn_invalid(self):
        """Test that invalid ISBN is rejected."""
        self.assertFalse(validate_isbn("invalid"))
        self.assertFalse(validate_isbn("123"))
    
    def test_normalize_isbn(self):
        """Test ISBN normalization removes spaces and hyphens."""
        self.assertEqual(normalize_isbn("978-0-596-52068-7"), "9780596520687")
        self.assertEqual(normalize_isbn("0-596-52068-9"), "0596520689")


class ISBNModelSmokeTest(TestCase):
    """Smoke tests for ISBN field in Book model."""
    
    def test_create_book_with_valid_isbn(self):
        """Test that a book can be created with a valid ISBN."""
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            course="Test Course",
            isbn="9780596520687"
        )
        self.assertIsNotNone(book.id)
        self.assertEqual(book.isbn, "9780596520687")
    
    def test_create_book_without_isbn(self):
        """Test that a book can be created without an ISBN."""
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            course="Test Course"
        )
        self.assertIsNotNone(book.id)
        self.assertIsNone(book.isbn)


class ISBNAPISmokeTest(TestCase):
    """Smoke tests for ISBN functionality in API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')
    
    def test_register_book_api_with_valid_isbn(self):
        """Test registering a book via API with valid ISBN."""
        response = self.client.post(
            reverse('register_book_api'),
            data=json.dumps({
                'title': 'Test Book',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978-0-596-52068-7'
            }),
            content_type='application/json'
        )
        
        # Debug: print response if it fails
        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content.decode()}")
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('book', data)
        self.assertEqual(data['book']['isbn'], '9780596520687')  # Normalized
    
    def test_register_book_api_with_invalid_isbn(self):
        """Test that API rejects invalid ISBN with 400."""
        response = self.client.post(
            reverse('register_book_api'),
            data=json.dumps({
                'title': 'Test Book',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': 'invalid-isbn'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Invalid ISBN', data['error'])
    
    def test_book_list_api_includes_isbn(self):
        """Test that book list API includes ISBN field."""
        Book.objects.create(
            title='Test Book',
            author='Test Author',
            course='Test Course',
            isbn='9780596520687'
        )
        
        response = self.client.get(reverse('book_list_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('books', data)
        self.assertTrue(len(data['books']) > 0)
        self.assertIn('isbn', data['books'][0])
