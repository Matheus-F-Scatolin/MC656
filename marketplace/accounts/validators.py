"""
Password validation utilities for user registration.
"""
import re


def validate_password(password):
    """
    Validate password strength based on the following requirements:
    - Between 6 and 15 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Args:
        password (str): The password to validate
        
    Returns:
        tuple: (is_valid (bool), error_message (str or None))
    """
    if not password:
        return False, "Password is required."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    if len(password) > 15:
        return False, "Password must be no more than 15 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    
    # Special characters: anything that's not a letter or digit
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "Password must contain at least one special character."
    
    return True, None


def get_password_requirements():
    """
    Return a list of password requirements for display purposes.
    
    Returns:
        list: List of password requirement strings
    """
    return [
        "Between 6 and 15 characters long",
        "Contains at least one uppercase letter (A-Z)",
        "Contains at least one lowercase letter (a-z)",
        "Contains at least one digit (0-9)",
        "Contains at least one special character (!@#$%^&*, etc.)"
    ]
