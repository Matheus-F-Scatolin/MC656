"""
Unit 1: ISBN Utility Functions Testing (Decision Table Approach)
Tests for validate_isbn() and normalize_isbn() using Decision Table technique.
Reference: ISBN_DECISION_TABLE.md
"""

import unittest
from books.utils import validate_isbn, normalize_isbn


class ISBNValidationDecisionTableTests(unittest.TestCase):
    """
    Unit tests for ISBN validation using Decision Table methodology.
    Tests all 15 rules from the decision table covering various input combinations.
    """
    
    # ===== RULE R1: Empty/Null ISBN =====
    def test_r1_empty_string(self):
        """R1: Empty string should return False (field validation happens at model level)."""
        self.assertFalse(validate_isbn(""))
    
    def test_r1_none_value(self):
        """R1: None value should return False."""
        self.assertFalse(validate_isbn(None))
    
    def test_r1_whitespace_only(self):
        """R1: Whitespace-only string should return False."""
        self.assertFalse(validate_isbn("   "))
        self.assertFalse(validate_isbn("\t\n"))
    
    # ===== RULE R2: Valid ISBN-10 =====
    def test_r2_valid_isbn10_numeric(self):
        """R2: Valid ISBN-10 with all digits should be accepted."""
        self.assertTrue(validate_isbn("0596520689"))
    
    def test_r2_valid_isbn10_with_x(self):
        """R2: Valid ISBN-10 ending with X should be accepted."""
        self.assertTrue(validate_isbn("043942089X"))
        self.assertTrue(validate_isbn("043942089x"))  # lowercase x
    
    def test_r2_valid_isbn10_another(self):
        """R2: Another valid ISBN-10 example."""
        self.assertTrue(validate_isbn("0123456789"))
    
    # ===== RULE R3: Bad Checksum ISBN-10 =====
    def test_r3_isbn10_invalid_checksum(self):
        """R3: ISBN-10 with invalid checksum should be rejected."""
        self.assertFalse(validate_isbn("0596520680"))  # Last digit wrong
    
    def test_r3_isbn10_invalid_checksum_with_x(self):
        """R3: ISBN-10 with X in wrong position for checksum."""
        self.assertFalse(validate_isbn("0596520688"))  # Should be 9, not 8
    
    # ===== RULE R4: Invalid Characters ISBN-10 =====
    def test_r4_isbn10_invalid_letter(self):
        """R4: ISBN-10 with invalid letter (not X at end) should be rejected."""
        self.assertFalse(validate_isbn("059652068A"))
        self.assertFalse(validate_isbn("A596520689"))
    
    def test_r4_isbn10_x_not_at_end(self):
        """R4: ISBN-10 with X not at the end should be rejected."""
        self.assertFalse(validate_isbn("059X520689"))
    
    def test_r4_isbn10_special_chars(self):
        """R4: ISBN-10 with special characters should be rejected."""
        self.assertFalse(validate_isbn("059@520689"))
        self.assertFalse(validate_isbn("059#520689"))
    
    # ===== RULE R5: Wrong Length (near 10) =====
    def test_r5_too_short_for_isbn10(self):
        """R5: 9 digits should be rejected."""
        self.assertFalse(validate_isbn("123456789"))
    
    def test_r5_too_long_for_isbn10(self):
        """R5: 11 digits should be rejected."""
        self.assertFalse(validate_isbn("12345678901"))
    
    def test_r5_twelve_digits(self):
        """R5: 12 digits should be rejected (not 10 or 13)."""
        self.assertFalse(validate_isbn("123456789012"))
    
    # ===== RULE R6: Valid ISBN-13 =====
    def test_r6_valid_isbn13(self):
        """R6: Valid ISBN-13 should be accepted."""
        self.assertTrue(validate_isbn("9780596520687"))
    
    def test_r6_valid_isbn13_another(self):
        """R6: Another valid ISBN-13."""
        self.assertTrue(validate_isbn("9781234567897"))
    
    def test_r6_valid_isbn13_third(self):
        """R6: Third valid ISBN-13 example."""
        self.assertTrue(validate_isbn("9780134685991"))
    
    # ===== RULE R7: Bad Checksum ISBN-13 =====
    def test_r7_isbn13_invalid_checksum(self):
        """R7: ISBN-13 with invalid checksum should be rejected."""
        self.assertFalse(validate_isbn("9780596520680"))  # Last digit wrong
    
    def test_r7_isbn13_invalid_checksum_another(self):
        """R7: Another ISBN-13 with bad checksum."""
        self.assertFalse(validate_isbn("9781234567890"))  # Should be 7, not 0
    
    # ===== RULE R8: Invalid Characters ISBN-13 =====
    def test_r8_isbn13_with_letter_x(self):
        """R8: ISBN-13 cannot have X (only ISBN-10 can)."""
        self.assertFalse(validate_isbn("978059652068X"))
    
    def test_r8_isbn13_with_other_letters(self):
        """R8: ISBN-13 with letters should be rejected."""
        self.assertFalse(validate_isbn("978A596520687"))
        self.assertFalse(validate_isbn("978059652068A"))
    
    def test_r8_isbn13_special_chars(self):
        """R8: ISBN-13 with special characters should be rejected."""
        self.assertFalse(validate_isbn("978@596520687"))
        self.assertFalse(validate_isbn("978#596520687"))
    
    # ===== RULE R9: Wrong Length (near 13) =====
    def test_r9_isbn13_too_short(self):
        """R9: 12 digits should be rejected for ISBN-13."""
        self.assertFalse(validate_isbn("978059652068"))
    
    def test_r9_isbn13_too_long(self):
        """R9: 14 digits should be rejected."""
        self.assertFalse(validate_isbn("97805965206870"))
    
    # ===== RULE R11: Valid ISBN-13 with Hyphens =====
    def test_r11_isbn13_with_hyphens(self):
        """R11: ISBN-13 with hyphens should be accepted after normalization."""
        self.assertTrue(validate_isbn("978-0-596-52068-7"))
    
    def test_r11_isbn10_with_hyphens(self):
        """R11: ISBN-10 with hyphens should be accepted after normalization."""
        self.assertTrue(validate_isbn("0-596-52068-9"))
    
    # ===== RULE R12: Valid ISBN with Spaces =====
    def test_r12_isbn10_with_spaces(self):
        """R12: ISBN-10 with spaces should be accepted after normalization."""
        self.assertTrue(validate_isbn("0 596 52068 9"))
    
    def test_r12_isbn13_with_spaces(self):
        """R12: ISBN-13 with spaces should be accepted after normalization."""
        self.assertTrue(validate_isbn("978 0 596 52068 7"))
    
    # ===== RULE R13: Mixed Separators =====
    def test_r13_mixed_hyphens_and_spaces(self):
        """R13: ISBN with mixed hyphens and spaces should be accepted."""
        self.assertTrue(validate_isbn("978 0-596-52068 7"))
        self.assertTrue(validate_isbn("0-596 520 68-9"))
    
    # ===== RULE R14: Invalid Special Characters =====
    def test_r14_isbn_with_prefix(self):
        """R14: ISBN with 'ISBN:' prefix should be rejected."""
        self.assertFalse(validate_isbn("ISBN:9780596520687"))
        self.assertFalse(validate_isbn("ISBN-13:9780596520687"))
    
    def test_r14_isbn_with_special_chars(self):
        """R14: ISBN with special characters should be rejected."""
        self.assertFalse(validate_isbn("978@0596#52068$7"))
        self.assertFalse(validate_isbn("978.0596.52068.7"))
    
    # ===== RULE R15: Extremely Short/Long =====
    def test_r15_very_short(self):
        """R15: Very short strings should be rejected."""
        self.assertFalse(validate_isbn("123"))
        self.assertFalse(validate_isbn("1"))
    
    def test_r15_very_long(self):
        """R15: Very long strings should be rejected."""
        self.assertFalse(validate_isbn("12345678901234567890"))
        self.assertFalse(validate_isbn("9" * 20))


class ISBNNormalizationTests(unittest.TestCase):
    """Tests for normalize_isbn() function."""
    
    def test_normalize_removes_hyphens(self):
        """Normalization should remove hyphens."""
        self.assertEqual(normalize_isbn("978-0-596-52068-7"), "9780596520687")
    
    def test_normalize_removes_spaces(self):
        """Normalization should remove spaces."""
        self.assertEqual(normalize_isbn("978 0 596 52068 7"), "9780596520687")
    
    def test_normalize_removes_mixed_separators(self):
        """Normalization should remove both hyphens and spaces."""
        self.assertEqual(normalize_isbn("978 0-596-52068 7"), "9780596520687")
    
    def test_normalize_converts_to_uppercase(self):
        """Normalization should convert lowercase 'x' to uppercase."""
        self.assertEqual(normalize_isbn("043942089x"), "043942089X")
    
    def test_normalize_empty_string(self):
        """Normalization of empty string should return empty string."""
        self.assertEqual(normalize_isbn(""), "")
    
    def test_normalize_none(self):
        """Normalization of None should return empty string."""
        self.assertEqual(normalize_isbn(None), "")
    
    def test_normalize_already_normalized(self):
        """Already normalized ISBN should remain unchanged."""
        self.assertEqual(normalize_isbn("9780596520687"), "9780596520687")
        self.assertEqual(normalize_isbn("0596520689"), "0596520689")


if __name__ == '__main__':
    unittest.main()
