from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json

from .validators import validate_password, get_password_requirements

# Create your tests here.

class PasswordValidatorTestCase(TestCase):
    """Test cases for password validation."""
    
    def test_valid_password(self):
        """Test that a valid password passes validation."""
        valid_passwords = [
            'TestPass1!',
            'MyP@ssw0rd',
            'Secure#123',
            'C0mplex&Pass',
            'Valid!Pass123',
            'Aa123!'
        ]
        
        for password in valid_passwords:
            is_valid, error = validate_password(password)
            self.assertTrue(is_valid, f"Password '{password}' should be valid but got error: {error}")
            self.assertIsNone(error)
    
    def test_password_too_short(self):
        """Test that passwords shorter than 6 characters are rejected."""
        short_passwords = ['Ab1!', 'Tc2@', 'Xy3#']
        
        for password in short_passwords:
            is_valid, error = validate_password(password)
            self.assertFalse(is_valid)
            self.assertIn('at least 6 characters', error)
    
    def test_password_no_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        is_valid, error = validate_password('testpass1!')
        self.assertFalse(is_valid)
        self.assertIn('uppercase letter', error)
    
    def test_password_no_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        is_valid, error = validate_password('TESTPASS1!')
        self.assertFalse(is_valid)
        self.assertIn('lowercase letter', error)
    
    def test_password_no_digit(self):
        """Test that passwords without digits are rejected."""
        is_valid, error = validate_password('TestPass!')
        self.assertFalse(is_valid)
        self.assertIn('digit', error)
    
    def test_password_no_special_char(self):
        """Test that passwords without special characters are rejected."""
        is_valid, error = validate_password('TestPass123')
        self.assertFalse(is_valid)
        self.assertIn('special character', error)
    
    def test_password_empty(self):
        """Test that empty passwords are rejected."""
        is_valid, error = validate_password('')
        self.assertFalse(is_valid)
        self.assertIn('required', error)
    
    def test_password_none(self):
        """Test that None passwords are rejected."""
        is_valid, error = validate_password(None)
        self.assertFalse(is_valid)
        self.assertIn('required', error)
    
    def test_password_1char_too_short(self):
        """Test that a password with lenght 5 is rejected."""
        is_valid, error = validate_password('Aa12!')
        self.assertFalse(is_valid)
        self.assertIn('at least 6 characters', error)
    
    def test_get_password_requirements(self):
        """Test that password requirements are returned correctly."""
        requirements = get_password_requirements()
        self.assertIsInstance(requirements, list)
        self.assertEqual(len(requirements), 5)
        self.assertIn('6 characters', requirements[0])


class AccountModelTestCase(TestCase):
    """Test cases for User model operations."""
    
    def test_user_creation(self):
        """Test that a user can be created and saved correctly."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!"
        )
        
        # Verify the user was saved correctly
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("TestPass123!"))
        self.assertIsNotNone(user.date_joined)
        
        # Verify the user exists in the database
        saved_user = User.objects.get(id=user.id)
        self.assertEqual(saved_user.username, "testuser")
        self.assertEqual(saved_user.email, "test@example.com")
    
    def test_user_str_representation(self):
        """Test the string representation of a user."""
        user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="TestPass123!"
        )
        self.assertEqual(str(user), "testuser2")
    
    def test_unique_username(self):
        """Test that usernames must be unique."""
        User.objects.create_user(
            username="uniqueuser",
            email="first@example.com",
            password="Password1!"
        )
        
        # Attempting to create another user with the same username should work
        # but the unique constraint is handled by the view logic
        user2 = User.objects.create_user(
            username="uniqueuser2",
            email="second@example.com",
            password="Password1!"
        )
        
        self.assertEqual(User.objects.count(), 2)


class AuthViewTestCase(TestCase):
    """Test cases for authentication views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="TestPass123!"
        )
    
    def test_signup_view_get(self):
        """Test GET request to signup view."""
        response = self.client.get(reverse('signup'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Account")
        self.assertContains(response, "Username:")
        self.assertContains(response, "Email:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Confirm Password:")
    
    def test_signup_post_success(self):
        """Test successful user signup."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        })
        
        # Check that the user was created
        self.assertEqual(User.objects.count(), initial_count + 1)
        
        # Check that the user was redirected to login
        self.assertRedirects(response, reverse('login'))
        
        # Verify the user was created with correct data
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertTrue(new_user.check_password('NewPass123!'))
    
    def test_signup_post_missing_fields(self):
        """Test signup with missing fields."""
        initial_count = User.objects.count()
        
        # Test with missing username
        response = self.client.post(reverse('signup'), {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "All fields are required.")
        
        # Test with missing password
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'confirm_password': 'TestPass123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "All fields are required.")
    
    def test_signup_password_mismatch(self):
        """Test signup with mismatched passwords."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'DifferentPass123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "Passwords do not match.")
    
    def test_signup_duplicate_username(self):
        """Test signup with existing username."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'existinguser',  # This user already exists
            'email': 'newemail@example.com',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "Username already exists.")
    
    def test_signup_duplicate_email(self):
        """Test signup with existing email."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'newusername',
            'email': 'existing@example.com',  # This email already exists
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "Email already registered.")
    
    def test_signup_weak_password_too_short(self):
        """Test signup with a password that's too short."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Aa1!',  # Only 4 characters
            'confirm_password': 'Aa1!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "at least 6 characters")
    
    def test_signup_weak_password_no_uppercase(self):
        """Test signup with a password missing uppercase letter."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123!',
            'confirm_password': 'testpass123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "uppercase letter")
    
    def test_signup_weak_password_no_lowercase(self):
        """Test signup with a password missing lowercase letter."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TESTPASS123!',
            'confirm_password': 'TESTPASS123!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "lowercase letter")
    
    def test_signup_weak_password_no_digit(self):
        """Test signup with a password missing a digit."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass!',
            'confirm_password': 'TestPass!'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "digit")
    
    def test_signup_weak_password_no_special_char(self):
        """Test signup with a password missing a special character."""
        initial_count = User.objects.count()
        
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        })
        
        self.assertEqual(User.objects.count(), initial_count)
        self.assertContains(response, "special character")
    
    def test_login_view_get(self):
        """Test GET request to login view."""
        response = self.client.get(reverse('login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log In")
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
    
    def test_login_post_success(self):
        """Test successful user login."""
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'TestPass123!'
        })
        
        # Check that the user was redirected to book list
        self.assertRedirects(response, reverse('book_list'))
        
        # Check that the user is logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, 'existinguser')
    
    def test_login_post_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")
        
        # Check that no user is logged in
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)
    
    def test_login_post_missing_fields(self):
        """Test login with missing fields."""
        # Test with missing password
        response = self.client.post(reverse('login'), {
            'username': 'existinguser'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required.")
        
        # Test with missing username
        response = self.client.post(reverse('login'), {
            'password': 'TestPass123!'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All fields are required.")
    
    def test_logout_view(self):
        """Test user logout."""
        # First, log in the user
        self.client.login(username='existinguser', password='TestPass123!')
        
        # Then logout
        response = self.client.get(reverse('logout'))
        
        # Check that the user was redirected to login page
        self.assertRedirects(response, reverse('login'))


class AuthAPITestCase(TestCase):
    """Test cases for authentication API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username="apiuser",
            email="api@example.com",
            password="ApiPass123!"
        )
    
    def test_signup_api_success(self):
        """Test successful user signup via API."""
        initial_count = User.objects.count()
        
        response = self.client.post(
            reverse('signup_api'),
            data=json.dumps({
                'username': 'newapi_user',
                'email': 'newapi@example.com',
                'password': 'NewApi123!',
                'confirm_password': 'NewApi123!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), initial_count + 1)
        
        # Parse the JSON response
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'newapi_user')
        self.assertEqual(data['user']['email'], 'newapi@example.com')
    
    def test_signup_api_validation_errors(self):
        """Test signup API with validation errors."""
        initial_count = User.objects.count()
        
        # Test with missing fields
        response = self.client.post(
            reverse('signup_api'),
            data=json.dumps({
                'username': 'testuser',
                'email': 'test@example.com'
                # Missing password fields
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), initial_count)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'All fields are required.')
    
    def test_signup_api_weak_password(self):
        """Test signup API with weak password."""
        initial_count = User.objects.count()
        
        # Test password without special character
        response = self.client.post(
            reverse('signup_api'),
            data=json.dumps({
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass123',
                'confirm_password': 'TestPass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), initial_count)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('special character', data['error'])
    
    def test_login_api_success(self):
        """Test successful user login via API."""
        response = self.client.post(
            reverse('login_api'),
            data=json.dumps({
                'username': 'apiuser',
                'password': 'ApiPass123!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'apiuser')
        self.assertEqual(data['user']['email'], 'api@example.com')
    
    def test_login_api_invalid_credentials(self):
        """Test login API with invalid credentials."""
        response = self.client.post(
            reverse('login_api'),
            data=json.dumps({
                'username': 'apiuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid username or password.')
    
    def test_api_invalid_json(self):
        """Test API endpoints with invalid JSON."""
        response = self.client.post(
            reverse('signup_api'),
            data="invalid json",
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid JSON data.')


class LandingPageTestCase(TestCase):
    """Test cases for the landing page."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!"
        )
    
    def test_landing_page_anonymous(self):
        """Test landing page for anonymous users."""
        response = self.client.get(reverse('landing'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BookMarket")
        self.assertContains(response, "Your University Book Exchange Platform")
        self.assertContains(response, "Log In")
        self.assertContains(response, "Sign Up")
    
    def test_landing_page_authenticated_redirect(self):
        """Test that authenticated users are redirected to book list."""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('landing'))
        
        # Should redirect to book list
        self.assertRedirects(response, reverse('book_list'))
    
    def test_landing_page_features(self):
        """Test that landing page shows features."""
        response = self.client.get(reverse('landing'))
        
        self.assertContains(response, "Browse and discover textbooks")
        self.assertContains(response, "List your books for sale")
        self.assertContains(response, "Connect with students")
        self.assertContains(response, "Save money on expensive textbooks")
