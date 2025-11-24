"""
Unit 2: Book Model Testing with ISBN (Decision Table Approach)
Tests for Book model persistence and ISBN validation at model level.
Reference: ISBN_DECISION_TABLE.md
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from books.models import Book


class ISBNModelDecisionTableTests(TestCase):
    """
    Model-level tests for ISBN functionality using Decision Table methodology.
    Tests persistence, validation, normalization, and unique constraints.
    """
    
    # ===== RULE R1: Empty/Null ISBN (Optional Field) =====
    def test_r1_book_without_isbn(self):
        """R1: Book can be created without ISBN (optional field)."""
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            course="Test Course"
        )
        self.assertIsNotNone(book.id)
        self.assertIsNone(book.isbn)
    
    def test_r1_book_with_empty_string_isbn(self):
        """R1: Empty string ISBN should be stored as None."""
        book = Book.objects.create(
            title="Test Book 2",
            author="Test Author",
            course="Test Course",
            isbn=""
        )
        self.assertIsNone(book.isbn)
    
    # ===== RULE R2: Valid ISBN-10 =====
    def test_r2_book_with_valid_isbn10(self):
        """R2: Book with valid ISBN-10 can be created."""
        book = Book.objects.create(
            title="Test Book ISBN-10",
            author="Test Author",
            course="Test Course",
            isbn="0596520689"
        )
        self.assertIsNotNone(book.id)
        self.assertEqual(book.isbn, "0596520689")
    
    def test_r2_book_with_isbn10_x_checkdigit(self):
        """R2: Book with ISBN-10 ending in X can be created."""
        book = Book.objects.create(
            title="Test Book ISBN-10X",
            author="Test Author",
            course="Test Course",
            isbn="043942089X"
        )
        self.assertEqual(book.isbn, "043942089X")
    
    # ===== RULE R3: Bad Checksum ISBN-10 =====
    def test_r3_book_with_invalid_isbn10_checksum(self):
        """R3: Book with invalid ISBN-10 checksum should raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Book.objects.create(
                title="Test Book Bad ISBN-10",
                author="Test Author",
                course="Test Course",
                isbn="0596520680"  # Invalid checksum
            )
        self.assertIn('isbn', str(context.exception).lower())
    
    # ===== RULE R4: Invalid Characters ISBN-10 =====
    def test_r4_book_with_invalid_chars_isbn10(self):
        """R4: Book with invalid characters in ISBN-10 should raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Book.objects.create(
                title="Test Book Invalid Chars",
                author="Test Author",
                course="Test Course",
                isbn="059652068A"
            )
        self.assertIn('isbn', str(context.exception).lower())
    
    # ===== RULE R5: Wrong Length =====
    def test_r5_book_with_wrong_length_isbn(self):
        """R5: Book with wrong length ISBN should raise ValidationError."""
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Test Book Wrong Length",
                author="Test Author",
                course="Test Course",
                isbn="123456789"  # Only 9 digits
            )
    
    # ===== RULE R6: Valid ISBN-13 =====
    def test_r6_book_with_valid_isbn13(self):
        """R6: Book with valid ISBN-13 can be created."""
        book = Book.objects.create(
            title="Test Book ISBN-13",
            author="Test Author",
            course="Test Course",
            isbn="9780596520687"
        )
        self.assertIsNotNone(book.id)
        self.assertEqual(book.isbn, "9780596520687")
    
    def test_r6_book_with_another_valid_isbn13(self):
        """R6: Another valid ISBN-13 example."""
        book = Book.objects.create(
            title="Test Book ISBN-13 v2",
            author="Test Author",
            course="Test Course",
            isbn="9781234567897"
        )
        self.assertEqual(book.isbn, "9781234567897")
    
    # ===== RULE R7: Bad Checksum ISBN-13 =====
    def test_r7_book_with_invalid_isbn13_checksum(self):
        """R7: Book with invalid ISBN-13 checksum should raise ValidationError."""
        with self.assertRaises(ValidationError) as context:
            Book.objects.create(
                title="Test Book Bad ISBN-13",
                author="Test Author",
                course="Test Course",
                isbn="9780596520680"  # Invalid checksum
            )
        self.assertIn('isbn', str(context.exception).lower())
    
    # ===== RULE R8: Invalid Characters ISBN-13 =====
    def test_r8_book_with_letter_in_isbn13(self):
        """R8: Book with letter in ISBN-13 should raise ValidationError."""
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Test Book Invalid ISBN-13",
                author="Test Author",
                course="Test Course",
                isbn="978059652068X"  # X not allowed in ISBN-13
            )
    
    # ===== RULE R10: Duplicate ISBN =====
    def test_r10_duplicate_isbn13_rejected(self):
        """R10: Duplicate ISBN-13 should raise ValidationError (detected by full_clean)."""
        # Create first book with ISBN
        Book.objects.create(
            title="First Book",
            author="Author 1",
            course="Course 1",
            isbn="9780596520687"
        )
        
        # Attempt to create second book with same ISBN
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Second Book",
                author="Author 2",
                course="Course 2",
                isbn="9780596520687"  # Duplicate
            )
    
    def test_r10_duplicate_isbn10_rejected(self):
        """R10: Duplicate ISBN-10 should raise ValidationError (detected by full_clean)."""
        Book.objects.create(
            title="First Book ISBN-10",
            author="Author 1",
            course="Course 1",
            isbn="0596520689"
        )
        
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Second Book ISBN-10",
                author="Author 2",
                course="Course 2",
                isbn="0596520689"  # Duplicate
            )
    
    # ===== RULE R11: Valid ISBN with Hyphens (Normalization) =====
    def test_r11_isbn13_with_hyphens_normalized(self):
        """R11: ISBN-13 with hyphens should be normalized and stored without them."""
        book = Book.objects.create(
            title="Test Book Hyphens",
            author="Test Author",
            course="Test Course",
            isbn="978-0-596-52068-7"
        )
        # Should be stored normalized (without hyphens)
        self.assertEqual(book.isbn, "9780596520687")
    
    def test_r11_isbn10_with_hyphens_normalized(self):
        """R11: ISBN-10 with hyphens should be normalized."""
        book = Book.objects.create(
            title="Test Book Hyphens ISBN-10",
            author="Test Author",
            course="Test Course",
            isbn="0-596-52068-9"
        )
        self.assertEqual(book.isbn, "0596520689")
    
    # ===== RULE R12: Valid ISBN with Spaces (Normalization) =====
    def test_r12_isbn_with_spaces_normalized(self):
        """R12: ISBN with spaces should be normalized."""
        book = Book.objects.create(
            title="Test Book Spaces",
            author="Test Author",
            course="Test Course",
            isbn="978 0 596 52068 7"
        )
        self.assertEqual(book.isbn, "9780596520687")
    
    # ===== RULE R13: Mixed Separators (Normalization) =====
    def test_r13_isbn_mixed_separators_normalized(self):
        """R13: ISBN with mixed hyphens and spaces should be normalized."""
        book = Book.objects.create(
            title="Test Book Mixed",
            author="Test Author",
            course="Test Course",
            isbn="978 0-596-52068 7"
        )
        self.assertEqual(book.isbn, "9780596520687")
    
    # ===== Additional Model Tests =====
    def test_isbn_update_with_valid_value(self):
        """Test updating ISBN to a valid value."""
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            course="Test Course"
        )
        book.isbn = "9780596520687"
        book.save()
        
        book.refresh_from_db()
        self.assertEqual(book.isbn, "9780596520687")
    
    def test_isbn_update_to_invalid_rejected(self):
        """Test that updating to invalid ISBN is rejected."""
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            course="Test Course",
            isbn="9780596520687"
        )
        
        book.isbn = "invalid-isbn"
        with self.assertRaises(ValidationError):
            book.save()
    
    def test_lowercase_x_normalized_to_uppercase(self):
        """Test that lowercase 'x' in ISBN-10 is normalized to uppercase."""
        book = Book.objects.create(
            title="Test Book lowercase x",
            author="Test Author",
            course="Test Course",
            isbn="043942089x"  # lowercase x
        )
        self.assertEqual(book.isbn, "043942089X")  # Should be uppercase
    
    def test_multiple_books_without_isbn_allowed(self):
        """Test that multiple books without ISBN are allowed (no unique constraint issue)."""
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
        
        self.assertIsNone(book1.isbn)
        self.assertIsNone(book2.isbn)
        self.assertNotEqual(book1.id, book2.id)
