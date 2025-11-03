import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse

from .models import Book
from .search_strategies import (
    BookSearchService,
    TitleSearchStrategy,
    AuthorSearchStrategy,
    CourseSearchStrategy,
    CombinedSearchStrategy,
    AdvancedSearchStrategy
)


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



class BookViewTestCase(TestCase):
    """Test cases for book views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
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

    def test_book_list_view_authenticated(self):
        """Test that authenticated users can access the book list view."""
        self.client.login(username='testuser', password='testpassword123')
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

    def test_book_list_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse('book_list'))

        # Check that the user is redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_book_list_empty_authenticated(self):
        """Test book list view when no books exist (authenticated user)."""
        self.client.login(username='testuser', password='testpassword123')
        Book.objects.all().delete()
        response = self.client.get(reverse('book_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No books available yet")
        self.assertEqual(len(response.context['books']), 0)

    def test_register_book_get_authenticated(self):
        """Test GET request to register book view (authenticated)."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('register_book'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register a New Book")
        self.assertContains(response, "Book Title:")
        self.assertContains(response, "Author:")
        self.assertContains(response, "Related Course:")

    def test_register_book_get_unauthenticated(self):
        """Test that unauthenticated users cannot access register book page."""
        response = self.client.get(reverse('register_book'))

        # Check that the user is redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_register_book_post_success_authenticated(self):
        """Test successful book registration (authenticated)."""
        self.client.login(username='testuser', password='testpassword123')
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

    def test_register_book_post_missing_fields_authenticated(self):
        """Test book registration with missing fields (authenticated)."""
        self.client.login(username='testuser', password='testpassword123')
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

    def test_book_list_api_authenticated(self):
        """Test the API endpoint that returns books as JSON (authenticated)."""
        self.client.login(username='testuser', password='testpassword123')
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

    def test_book_list_api_unauthenticated(self):
        """Test that unauthenticated users cannot access the API."""
        response = self.client.get(reverse('book_list_api'))

        # Check that the user is redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class BookSearchTestCase(TestCase):
    """Test cases for book search functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        self.book1 = Book.objects.create(
            title="Python Programming",
            author="John Smith",
            course="CS101"
        )
        self.book2 = Book.objects.create(
            title="Data Structures",
            author="Jane Doe",
            course="CS201"
        )
        self.book3 = Book.objects.create(
            title="Machine Learning",
            author="Alice Johnson",
            course="CS301"
        )

    def test_search_books_view_authenticated(self):
        """Test that authenticated users can access the search books view."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search Books")
        self.assertContains(response, "All Books")
        self.assertEqual(len(response.context['books']), 3)

    def test_search_books_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse('search_books'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_search_books_by_title(self):
        """Test searching books by title."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': 'Python'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search results for "Python"')
        self.assertEqual(len(response.context['books']), 1)
        self.assertEqual(response.context['books'][0].title, "Python Programming")
        self.assertEqual(response.context['query'], 'Python')

    def test_search_books_by_author(self):
        """Test searching books by author."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': 'Jane'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search results for "Jane"')
        self.assertEqual(len(response.context['books']), 1)
        self.assertEqual(response.context['books'][0].author, "Jane Doe")

    def test_search_books_by_course(self):
        """Test searching books by course."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': 'CS201'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search results for "CS201"')
        self.assertEqual(len(response.context['books']), 1)
        self.assertEqual(response.context['books'][0].course, "CS201")

    def test_search_books_case_insensitive(self):
        """Test that search is case insensitive."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': 'python'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['books']), 1)
        self.assertEqual(response.context['books'][0].title, "Python Programming")

    def test_search_books_multiple_results(self):
        """Test search that returns multiple results."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': 'CS'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['books']), 3)  # All courses contain 'CS'

    def test_search_books_no_results(self):
        """Test search with no matching results."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': 'NonExistent'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['books']), 0)

    def test_search_books_empty_query(self):
        """Test search with empty query shows all books."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': ''})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Books")
        self.assertEqual(len(response.context['books']), 3)

    def test_search_books_whitespace_query(self):
        """Test search with whitespace-only query shows all books."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('search_books'), {'q': '   '})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['books']), 3)


class BookSearchServiceTestCase(TestCase):
    """Unit tests for the BookSearchService and its strategies."""

    def setUp(self):
        self.factory = RequestFactory()
        self.book1 = Book.objects.create(
            title="Python Programming",
            author="John Smith",
            course="CS101"
        )
        self.book2 = Book.objects.create(
            title="Data Structures",
            author="Jane Doe",
            course="CS201"
        )
        self.book3 = Book.objects.create(
            title="Machine Learning",
            author="Alice Johnson",
            course="CS301"
        )

    # --- Strategy-specific tests ---

    def test_title_search_strategy(self):
        request = self.factory.get("/books/search/?q=Python")
        results = TitleSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book1])

    def test_author_search_strategy(self):
        request = self.factory.get("/books/search/?q=Jane")
        results = AuthorSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book2])

    def test_course_search_strategy(self):
        request = self.factory.get("/books/search/?q=CS201")
        results = CourseSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book2])

    def test_combined_search_strategy(self):
        request = self.factory.get("/books/search/?q=Machine")
        results = CombinedSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book3])

        request = self.factory.get("/books/search/?q=CS")
        results = CombinedSearchStrategy().search(request)
        self.assertEqual(set(results), {self.book1, self.book2, self.book3})

    def test_advanced_search_strategy_partial_fields(self):
        # Only title filter
        request = self.factory.get("/books/search/?mode=advanced&title=Python&author=&course=")
        results = AdvancedSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book1])

        # Title + author filter (no match)
        request = self.factory.get("/books/search/?mode=advanced&title=Python&author=Jane&course=")
        results = AdvancedSearchStrategy().search(request)
        self.assertEqual(len(results), 0)

        # Author + course match
        request = self.factory.get("/books/search/?mode=advanced&title=&author=Jane&course=CS201")
        results = AdvancedSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book2])

    def test_book_search_service_dispatch(self):
        """Ensure BookSearchService delegates correctly based on mode."""
        # Title strategy
        request = self.factory.get("/books/search/?q=Python&mode=title")
        service = BookSearchService("title")
        results = service.search(request)
        self.assertEqual(list(results), [self.book1])

        # Advanced strategy
        request = self.factory.get("/books/search/?mode=advanced&title=Machine")
        service = BookSearchService("advanced")
        results = service.search(request)
        self.assertEqual(list(results), [self.book3])

        # Default (combined)
        request = self.factory.get("/books/search/?q=Jane")
        service = BookSearchService("nonexistent")  # fallback
        results = service.search(request)
        self.assertEqual(list(results), [self.book2])

    def test_case_insensitivity(self):
        request = self.factory.get("/books/search/?q=python")
        results = CombinedSearchStrategy().search(request)
        self.assertEqual(list(results), [self.book1])

    def test_empty_query_returns_all_combined(self):
        request = self.factory.get("/books/search/?q=")
        results = CombinedSearchStrategy().search(request)
        self.assertEqual(set(results), {self.book1, self.book2, self.book3})

    def test_empty_query_returns_none_for_specific_strategies(self):
        for strategy_cls in [TitleSearchStrategy, AuthorSearchStrategy, CourseSearchStrategy]:
            request = self.factory.get("/books/search/?q=")
            results = strategy_cls().search(request)
            self.assertEqual(len(results), 0)
