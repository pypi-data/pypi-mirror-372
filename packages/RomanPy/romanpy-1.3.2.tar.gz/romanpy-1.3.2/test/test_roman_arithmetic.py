"""
Test for RomanNumeral class arithmetic operations.
"""

from unittest import TestCase
from roman import roman


class TestRomanArithmetic(TestCase):
    """
    A testcase for the arithmetic operations of the RomanNumeral class.
    """

    def test_roman_add_roman(self):
        """
        Assert that a roman numeral can be added to another roman numeral.
        """
        self.assertEqual(2, roman(1) + roman(1))

    def test_roman_add_int(self):
        """
        Assert that a decimal can be added to a roman numeral.
        """
        self.assertEqual(2, roman(1) + 1)

    def test_roman_sub_roman(self):
        """
        Assert that a roman numeral can be subtracted
        from another roman numeral.
        """
        self.assertEqual(1, roman(2) - roman(1))

    def test_roman_sub_int(self):
        """
        Assert that a decimal can be subtracted from a roman numeral.
        """
        self.assertEqual(1, roman(2) - 1)

    def test_roman_mul_roman(self):
        """
        Assert that a roman numeral can be multiplied with another
        roman numeral.
        """
        self.assertEqual(2, roman(1) * roman(2))

    def test_roman_mul_int(self):
        """
        Assert that a roman numeral can be multiplied with decimal.
        """
        self.assertEqual(2, roman(1) * 2)

    def test_roman_truediv_roman(self):
        """
        Assert that a roman numeral can be true divided
        by another roman numeral.
        """
        self.assertEqual(1, roman(2) / roman(2))

    def test_roman_truediv_int(self):
        """
        Assert that a roman numeral can be true divided by a decimal.
        """
        self.assertEqual(1, roman(2) / 2)

    def test_roman_floordiv_roman(self):
        """
        Assert that a roman numeral can be floor divided
        by another roman numeral.
        """
        self.assertEqual(1, roman(2) // roman(2))

    def test_roman_floordiv_int(self):
        """
        Assert that a roman numeral can be floor divided by a decimal.
        """
        self.assertEqual(1, roman(2) // 2)
