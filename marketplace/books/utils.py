"""
Utility functions for the books app.
"""


def validate_isbn(isbn: str) -> bool:
    """
    Validate an ISBN-10 or ISBN-13 number.
    
    This function normalizes the input by removing spaces and hyphens,
    then validates the ISBN using the appropriate checksum algorithm.
    
    Args:
        isbn: String containing the ISBN to validate. Can include spaces and hyphens.
              For ISBN-10, the last character can be 'X' (representing 10).
    
    Returns:
        bool: True if the ISBN is valid, False otherwise.
    
    Examples:
        >>> validate_isbn("978-0-596-52068-7")
        True
        >>> validate_isbn("0-596-52068-9")
        True
        >>> validate_isbn("043942089X")
        True
        >>> validate_isbn("invalid")
        False
    """
    if not isbn:
        return False
    
    # Normalize: remove spaces, hyphens, and convert to uppercase
    normalized = isbn.replace(" ", "").replace("-", "").upper()
    
    # Check length (must be 10 or 13)
    length = len(normalized)
    if length not in [10, 13]:
        return False
    
    if length == 10:
        return _validate_isbn10(normalized)
    else:  # length == 13
        return _validate_isbn13(normalized)


def _validate_isbn10(isbn: str) -> bool:
    """
    Validate an ISBN-10 using the checksum algorithm.
    
    ISBN-10 checksum: sum of (digit * position) mod 11 must equal 0.
    Position counts from 10 down to 1.
    The last digit can be 'X' representing 10.
    
    Args:
        isbn: Normalized ISBN-10 string (10 characters, no spaces/hyphens).
    
    Returns:
        bool: True if valid, False otherwise.
    """
    if len(isbn) != 10:
        return False
    
    # First 9 characters must be digits
    if not isbn[:9].isdigit():
        return False
    
    # Last character can be digit or 'X'
    if not (isbn[9].isdigit() or isbn[9] == 'X'):
        return False
    
    # Calculate checksum
    checksum = 0
    for i in range(9):
        checksum += int(isbn[i]) * (10 - i)
    
    # Handle last digit (might be 'X')
    if isbn[9] == 'X':
        checksum += 10
    else:
        checksum += int(isbn[9])
    
    return checksum % 11 == 0


def _validate_isbn13(isbn: str) -> bool:
    """
    Validate an ISBN-13 using the checksum algorithm.
    
    ISBN-13 checksum: alternating weights of 1 and 3.
    (sum of digits with weights 1,3,1,3,...) mod 10 must equal 0.
    
    Args:
        isbn: Normalized ISBN-13 string (13 characters, no spaces/hyphens).
    
    Returns:
        bool: True if valid, False otherwise.
    """
    if len(isbn) != 13:
        return False
    
    # All characters must be digits
    if not isbn.isdigit():
        return False
    
    # Calculate checksum
    checksum = 0
    for i in range(13):
        digit = int(isbn[i])
        weight = 1 if i % 2 == 0 else 3
        checksum += digit * weight
    
    return checksum % 10 == 0


def normalize_isbn(isbn: str) -> str:
    """
    Normalize an ISBN by removing spaces and hyphens, keeping only digits and 'X'.
    
    Args:
        isbn: ISBN string to normalize.
    
    Returns:
        str: Normalized ISBN (uppercase, no spaces or hyphens).
    """
    if not isbn:
        return ""
    
    return isbn.replace(" ", "").replace("-", "").upper()
