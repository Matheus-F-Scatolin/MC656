"""
Unit 3: API Integration Testing with ISBN (Decision Table Approach)
Tests for register_book_api endpoint with ISBN validation.
Reference: ISBN_DECISION_TABLE.md
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from books.models import Book


class ISBNAPIDecisionTableTests(TestCase):
    """
    API integration tests for ISBN functionality using Decision Table methodology.
    Tests HTTP endpoints, JSON payloads, error responses, and success cases.
    """
    
    def setUp(self):
        """Set up test client and authenticated user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.api_url = reverse('register_book_api')
    
    # ===== RULE R1: Empty/Null ISBN (Optional Field) =====
    def test_r1_api_book_without_isbn(self):
        """R1: API should accept book creation without ISBN."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book No ISBN',
                'author': 'Test Author',
                'course': 'Test Course'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIsNone(data['book']['isbn'])
    
    def test_r1_api_book_with_empty_isbn(self):
        """R1: API should accept empty string as ISBN (treated as None)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Empty ISBN',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': ''
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIsNone(data['book']['isbn'])
    
    # ===== RULE R2: Valid ISBN-10 =====
    def test_r2_api_create_book_with_valid_isbn10(self):
        """R2: API should accept book with valid ISBN-10."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book ISBN-10',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '0596520689'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['book']['isbn'], '0596520689')
    
    def test_r2_api_isbn10_with_x_checkdigit(self):
        """R2: API should accept ISBN-10 with X as check digit."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book ISBN-10X',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '043942089X'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['book']['isbn'], '043942089X')
    
    # ===== RULE R3: Bad Checksum ISBN-10 =====
    def test_r3_api_reject_invalid_isbn10_checksum(self):
        """R3: API should reject ISBN-10 with invalid checksum (400)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Bad ISBN-10',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '0596520680'  # Invalid checksum
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('invalid', data['error'].lower())
    
    # ===== RULE R4: Invalid Characters ISBN-10 =====
    def test_r4_api_reject_invalid_chars_isbn10(self):
        """R4: API should reject ISBN-10 with invalid characters (400)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Invalid Chars',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '059652068A'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # ===== RULE R5: Wrong Length =====
    def test_r5_api_reject_wrong_length(self):
        """R5: API should reject ISBN with wrong length (400)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Wrong Length',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '123456789'  # Only 9 digits
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # ===== RULE R6: Valid ISBN-13 =====
    def test_r6_api_create_book_with_valid_isbn13(self):
        """R6: API should accept book with valid ISBN-13."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book ISBN-13',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '9780596520687'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data['book']['isbn'], '9780596520687')
    
    def test_r6_api_another_valid_isbn13(self):
        """R6: API should accept another valid ISBN-13."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book ISBN-13 v2',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '9781234567897'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['book']['isbn'], '9781234567897')
    
    # ===== RULE R7: Bad Checksum ISBN-13 =====
    def test_r7_api_reject_invalid_isbn13_checksum(self):
        """R7: API should reject ISBN-13 with invalid checksum (400)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Bad ISBN-13',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '9780596520680'  # Invalid checksum
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('invalid', data['error'].lower())
    
    # ===== RULE R8: Invalid Characters ISBN-13 =====
    def test_r8_api_reject_letter_in_isbn13(self):
        """R8: API should reject ISBN-13 with letters (400)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Invalid ISBN-13',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978059652068X'  # X not allowed in ISBN-13
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # ===== RULE R9: Wrong Length (near 13) =====
    def test_r9_api_reject_isbn13_wrong_length(self):
        """R9: API should reject 12-digit ISBN (too short for ISBN-13)."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book 12 Digits',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978059652068'  # Only 12 digits
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # ===== RULE R10: Duplicate ISBN =====
    def test_r10_api_reject_duplicate_isbn(self):
        """R10: API should reject duplicate ISBN (400)."""
        # Create first book
        self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'First Book',
                'author': 'Author 1',
                'course': 'Course 1',
                'isbn': '9780596520687'
            }),
            content_type='application/json'
        )
        
        # Try to create second book with same ISBN
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Second Book',
                'author': 'Author 2',
                'course': 'Course 2',
                'isbn': '9780596520687'  # Duplicate
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('already exists', data['error'].lower())
    
    # ===== RULE R11: Valid ISBN with Hyphens (Normalization) =====
    def test_r11_api_isbn13_with_hyphens(self):
        """R11: API should accept ISBN-13 with hyphens and normalize it."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Hyphens',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978-0-596-52068-7'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        # Should be normalized (no hyphens)
        self.assertEqual(data['book']['isbn'], '9780596520687')
    
    def test_r11_api_isbn10_with_hyphens(self):
        """R11: API should accept ISBN-10 with hyphens and normalize it."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book ISBN-10 Hyphens',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '0-596-52068-9'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['book']['isbn'], '0596520689')
    
    # ===== RULE R12: Valid ISBN with Spaces =====
    def test_r12_api_isbn_with_spaces(self):
        """R12: API should accept ISBN with spaces and normalize it."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Spaces',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978 0 596 52068 7'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['book']['isbn'], '9780596520687')
    
    # ===== RULE R13: Mixed Separators =====
    def test_r13_api_isbn_mixed_separators(self):
        """R13: API should accept ISBN with mixed hyphens and spaces."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Mixed',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978 0-596-52068 7'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['book']['isbn'], '9780596520687')
    
    # ===== RULE R14: Invalid Special Characters =====
    def test_r14_api_reject_isbn_with_prefix(self):
        """R14: API should reject ISBN with 'ISBN:' prefix."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Prefix',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': 'ISBN:9780596520687'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_r14_api_reject_special_characters(self):
        """R14: API should reject ISBN with special characters."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Special Chars',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '978@0596#52068$7'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # ===== RULE R15: Extremely Short/Long =====
    def test_r15_api_reject_very_short_isbn(self):
        """R15: API should reject very short ISBN strings."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Too Short',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_r15_api_reject_very_long_isbn(self):
        """R15: API should reject very long ISBN strings."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book Too Long',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '12345678901234567890'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    # ===== Additional API Tests =====
    def test_api_missing_required_fields(self):
        """API should return 400 when required fields are missing."""
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book',
                'isbn': '9780596520687'
                # Missing author and course
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_api_invalid_json(self):
        """API should return 400 for invalid JSON."""
        response = self.client.post(
            self.api_url,
            data='invalid json{',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_api_unauthenticated_rejected(self):
        """API should reject unauthenticated requests."""
        self.client.logout()
        response = self.client.post(
            self.api_url,
            data=json.dumps({
                'title': 'Test Book',
                'author': 'Test Author',
                'course': 'Test Course',
                'isbn': '9780596520687'
            }),
            content_type='application/json'
        )
        
        # Should redirect to login (302) or return 401/403
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_api_book_list_includes_isbn(self):
        """Test that book_list_api includes ISBN in response."""
        Book.objects.create(
            title='Test Book with ISBN',
            author='Test Author',
            course='Test Course',
            isbn='9780596520687'
        )
        
        response = self.client.get(reverse('book_list_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('books', data)
        self.assertTrue(len(data['books']) > 0)
        
        # Check that ISBN field is present
        for book in data['books']:
            self.assertIn('isbn', book)
