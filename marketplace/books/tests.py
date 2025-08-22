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


class BookSearchTestCase(TestCase):
    """Test cases for book search functionality."""
    
    def setUp(self):
        """Set up test data for search tests."""
        self.client = Client()
        
        # Create test books with diverse data for comprehensive search testing
        self.book1 = Book.objects.create(
            title="Introduction to Python Programming",
            author="John Smith",
            course="Computer Science 101"
        )
        self.book2 = Book.objects.create(
            title="Advanced Java Development",
            author="Jane Doe",
            course="Software Engineering 201"
        )
        self.book3 = Book.objects.create(
            title="Data Structures and Algorithms",
            author="Bob Johnson",
            course="Computer Science 102"
        )
        self.book4 = Book.objects.create(
            title="Machine Learning Fundamentals",
            author="Alice Brown",
            course="Artificial Intelligence 301"
        )
        self.book5 = Book.objects.create(
            title="Web Development with Python",
            author="Charlie Wilson",
            course="Web Development 250"
        )
    
    def test_search_books_get_request(self):
        """Test GET request to search books view without query."""
        response = self.client.get(reverse('search_books'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search Books")
        self.assertContains(response, "Search by title, author, or course:")
        self.assertEqual(len(response.context['books']), 0)
        self.assertEqual(response.context['query'], '')
    
    def test_search_books_by_title(self):
        """Test searching books by title."""
        # Search for "Python" - should find 2 books
        response = self.client.get(reverse('search_books'), {'q': 'Python'})
        
        self.assertEqual(response.status_code, 200)
        books = response.context['books']
        self.assertEqual(len(books), 2)
        self.assertEqual(response.context['query'], 'Python')
        
        titles = [book.title for book in books]
        self.assertIn("Introduction to Python Programming", titles)
        self.assertIn("Web Development with Python", titles)
        
        # Search for exact title
        response = self.client.get(reverse('search_books'), {'q': 'Advanced Java Development'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Advanced Java Development")
    
    def test_search_books_by_author(self):
        """Test searching books by author name."""
        # Search for "John" - should find 1 book
        response = self.client.get(reverse('search_books'), {'q': 'John'})
        
        self.assertEqual(response.status_code, 200)
        books = response.context['books']
        self.assertEqual(len(books), 2)  # John Smith and Bob Johnson
        self.assertEqual(response.context['query'], 'John')
        
        authors = [book.author for book in books]
        self.assertIn("John Smith", authors)
        self.assertIn("Bob Johnson", authors)
        
        # Search for exact author name
        response = self.client.get(reverse('search_books'), {'q': 'Jane Doe'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].author, "Jane Doe")
    
    def test_search_books_by_course(self):
        """Test searching books by course name."""
        # Search for "Computer Science" - should find 2 books
        response = self.client.get(reverse('search_books'), {'q': 'Computer Science'})
        
        self.assertEqual(response.status_code, 200)
        books = response.context['books']
        self.assertEqual(len(books), 2)
        self.assertEqual(response.context['query'], 'Computer Science')
        
        courses = [book.course for book in books]
        self.assertIn("Computer Science 101", courses)
        self.assertIn("Computer Science 102", courses)
        
        # Search for specific course number
        response = self.client.get(reverse('search_books'), {'q': '301'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].course, "Artificial Intelligence 301")
    
    def test_search_books_case_insensitive(self):
        """Test that search is case-insensitive."""
        # Test lowercase search
        response = self.client.get(reverse('search_books'), {'q': 'python'})
        books = response.context['books']
        self.assertEqual(len(books), 2)
        
        # Test uppercase search
        response = self.client.get(reverse('search_books'), {'q': 'PYTHON'})
        books = response.context['books']
        self.assertEqual(len(books), 2)
        
        # Test mixed case search
        response = self.client.get(reverse('search_books'), {'q': 'PyThOn'})
        books = response.context['books']
        self.assertEqual(len(books), 2)
    
    def test_search_books_partial_match(self):
        """Test that search works with partial matches."""
        # Search for partial title
        response = self.client.get(reverse('search_books'), {'q': 'Data'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Data Structures and Algorithms")
        
        # Search for partial author
        response = self.client.get(reverse('search_books'), {'q': 'Alice'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].author, "Alice Brown")
        
        # Search for partial course
        response = self.client.get(reverse('search_books'), {'q': 'Web'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].course, "Web Development 250")
    
    def test_search_books_no_results(self):
        """Test searching with query that returns no results."""
        response = self.client.get(reverse('search_books'), {'q': 'NonexistentBook'})
        
        self.assertEqual(response.status_code, 200)
        books = response.context['books']
        self.assertEqual(len(books), 0)
        self.assertEqual(response.context['query'], 'NonexistentBook')
        self.assertContains(response, "No books found for")
    
    def test_search_books_empty_query(self):
        """Test searching with empty query."""
        response = self.client.get(reverse('search_books'), {'q': ''})
        
        self.assertEqual(response.status_code, 200)
        books = response.context['books']
        self.assertEqual(len(books), 0)
        self.assertEqual(response.context['query'], '')
    
    def test_search_books_whitespace_query(self):
        """Test searching with whitespace-only query."""
        response = self.client.get(reverse('search_books'), {'q': '   '})
        
        self.assertEqual(response.status_code, 200)
        books = response.context['books']
        self.assertEqual(len(books), 0)
        self.assertEqual(response.context['query'], '')
    
    def test_search_books_api(self):
        """Test the search API endpoint."""
        response = self.client.get(reverse('search_books_api'), {'q': 'Python'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        
        # Check the structure of the response
        self.assertIn('books', data)
        self.assertIn('query', data)
        self.assertIn('count', data)
        
        self.assertEqual(data['query'], 'Python')
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['books']), 2)
        
        # Check that the correct books are returned
        titles = [book['title'] for book in data['books']]
        self.assertIn("Introduction to Python Programming", titles)
        self.assertIn("Web Development with Python", titles)
    
    def test_search_books_api_no_query(self):
        """Test the search API endpoint without query parameter."""
        response = self.client.get(reverse('search_books_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['query'], '')
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['books']), 0)
    
    def test_search_books_api_empty_results(self):
        """Test the search API endpoint with query that returns no results."""
        response = self.client.get(reverse('search_books_api'), {'q': 'NonexistentBook'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['query'], 'NonexistentBook')
        self.assertEqual(data['count'], 0)
        self.assertEqual(len(data['books']), 0)
    
    def test_search_books_multiple_words(self):
        """Test searching with multiple words."""
        # Search for multiple words that should match
        response = self.client.get(reverse('search_books'), {'q': 'Machine Learning'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Machine Learning Fundamentals")
        
        # Search for a single word that should find multiple books
        response = self.client.get(reverse('search_books'), {'q': 'John'})
        books = response.context['books']
        # Should find books with "John" in author name (John Smith, Bob Johnson)
        self.assertEqual(len(books), 2)
        authors = [book.author for book in books]
        self.assertIn("John Smith", authors)
        self.assertIn("Bob Johnson", authors)
    
    def test_search_books_special_characters(self):
        """Test searching with special characters."""
        # Create a book with special characters for testing
        special_book = Book.objects.create(
            title="C++ Programming & Design",
            author="Dr. Smith-Jones",
            course="CS-301: Advanced Programming"
        )
        
        # Search for the special characters
        response = self.client.get(reverse('search_books'), {'q': 'C++'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], special_book)
        
        response = self.client.get(reverse('search_books'), {'q': 'Smith-Jones'})
        books = response.context['books']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0], special_book)
    
    def test_search_books_ordering(self):
        """Test that search results maintain proper ordering (newest first)."""
        # Search for a term that matches multiple books
        response = self.client.get(reverse('search_books'), {'q': 'Computer Science'})
        books = response.context['books']
        
        # Verify that books are ordered by creation date (newest first)
        self.assertEqual(len(books), 2)
        # book3 (CS 102) was created after book1 (CS 101), so it should come first
        self.assertEqual(books[0], self.book3)
        self.assertEqual(books[1], self.book1)
