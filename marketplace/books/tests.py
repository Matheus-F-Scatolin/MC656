from django.test import TestCase, Client
from django.urls import reverse
from .models import Book
import json

# Create your tests here.

class BookModelTestCase(TestCase):
    """Test cases for the Book model."""
    
    def test_book_creation(self):
        """Test that a book can be created and saved correctly."""
        book = Book.objects.create(
            title="Introduction to Computer Science",
            author="John Smith",
            course="CS101"
        )
        
        # Verify the book was saved correctly
        self.assertEqual(book.title, "Introduction to Computer Science")
        self.assertEqual(book.author, "John Smith")
        self.assertEqual(book.course, "CS101")
        self.assertIsNotNone(book.created_at)
        self.assertIsNotNone(book.updated_at)
        
        # Verify the book exists in the database
        saved_book = Book.objects.get(id=book.id)
        self.assertEqual(saved_book.title, "Introduction to Computer Science")
        self.assertEqual(saved_book.author, "John Smith")
        self.assertEqual(saved_book.course, "CS101")
    
    def test_book_str_representation(self):
        """Test the string representation of a book."""
        book = Book.objects.create(
            title="Python Programming",
            author="Jane Doe",
            course="CS102"
        )
        self.assertEqual(str(book), "Python Programming by Jane Doe")
    
    def test_book_ordering(self):
        """Test that books are ordered by creation date (newest first)."""
        book1 = Book.objects.create(
            title="Book 1",
            author="Author 1",
            course="Course 1"
        )
        book2 = Book.objects.create(
            title="Book 2",
            author="Author 2",
            course="Course 2"
        )
        
        books = list(Book.objects.all())
        self.assertEqual(books[0], book2)  # Newest first
        self.assertEqual(books[1], book1)


class BookViewTestCase(TestCase):
    """Test cases for book views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.book1 = Book.objects.create(
            title="Test Book 1",
            author="Test Author 1",
            course="Test Course 1"
        )
        self.book2 = Book.objects.create(
            title="Test Book 2",
            author="Test Author 2",
            course="Test Course 2"
        )
    
    def test_book_list_view(self):
        """Test that the book list view returns all books."""
        response = self.client.get(reverse('book_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that both books are in the context
        self.assertContains(response, "Test Book 1")
        self.assertContains(response, "Test Book 2")
        self.assertContains(response, "Test Author 1")
        self.assertContains(response, "Test Author 2")
        self.assertContains(response, "Test Course 1")
        self.assertContains(response, "Test Course 2")
        
        # Check that the books are in the context
        books = response.context['books']
        self.assertEqual(len(books), 2)
        self.assertIn(self.book1, books)
        self.assertIn(self.book2, books)
    
    def test_book_list_empty(self):
        """Test book list view when no books exist."""
        Book.objects.all().delete()
        response = self.client.get(reverse('book_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No books available yet")
        self.assertEqual(len(response.context['books']), 0)
    
    def test_register_book_get(self):
        """Test GET request to register book view."""
        response = self.client.get(reverse('register_book'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register a New Book")
        self.assertContains(response, "Book Title:")
        self.assertContains(response, "Author:")
        self.assertContains(response, "Related Course:")
    
    def test_register_book_post_success(self):
        """Test successful book registration."""
        initial_count = Book.objects.count()
        
        response = self.client.post(reverse('register_book'), {
            'title': 'New Test Book',
            'author': 'New Test Author',
            'course': 'New Test Course'
        })
        
        # Check that the book was created
        self.assertEqual(Book.objects.count(), initial_count + 1)
        
        # Check that the user was redirected to the book list
        self.assertRedirects(response, reverse('book_list'))
        
        # Verify the book was created with correct data
        new_book = Book.objects.get(title='New Test Book')
        self.assertEqual(new_book.author, 'New Test Author')
        self.assertEqual(new_book.course, 'New Test Course')
    
    def test_register_book_post_missing_fields(self):
        """Test book registration with missing fields."""
        initial_count = Book.objects.count()
        
        # Test with missing title
        response = self.client.post(reverse('register_book'), {
            'author': 'Test Author',
            'course': 'Test Course'
        })
        
        # Check that no book was created
        self.assertEqual(Book.objects.count(), initial_count)
        
        # Check that an error message is displayed
        self.assertContains(response, "All fields are required.")
        
        # Test with missing author
        response = self.client.post(reverse('register_book'), {
            'title': 'Test Title',
            'course': 'Test Course'
        })
        
        self.assertEqual(Book.objects.count(), initial_count)
        self.assertContains(response, "All fields are required.")
        
        # Test with missing course
        response = self.client.post(reverse('register_book'), {
            'title': 'Test Title',
            'author': 'Test Author'
        })
        
        self.assertEqual(Book.objects.count(), initial_count)
        self.assertContains(response, "All fields are required.")
    
    def test_book_list_api(self):
        """Test the API endpoint that returns books as JSON."""
        response = self.client.get(reverse('book_list_api'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check the structure of the response
        self.assertIn('books', data)
        self.assertEqual(len(data['books']), 2)
        
        # Check the first book data
        book_data = data['books'][0]
        self.assertIn('id', book_data)
        self.assertIn('title', book_data)
        self.assertIn('author', book_data)
        self.assertIn('course', book_data)
        self.assertIn('created_at', book_data)
        self.assertIn('updated_at', book_data)
        
        # Verify the actual data (books are ordered by creation date, newest first)
        titles = [book['title'] for book in data['books']]
        self.assertIn('Test Book 1', titles)
        self.assertIn('Test Book 2', titles)
