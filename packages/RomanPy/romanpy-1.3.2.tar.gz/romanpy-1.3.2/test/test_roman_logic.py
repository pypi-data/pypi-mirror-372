"""
Test for the RomanNumeral class logical operations.
"""

from unittest import TestCase
from roman import roman


class TestRomanLogic(TestCase):
    """
    A testcase for logical operations on the RomanNumeral class.
    """

    def test_roman_eq_roman(self):
        """
        Assert that two roman numerals of equal value are equal.
        """
        self.assertEqual(roman(1), roman(1))

    def test_roman_ne_roman(self):
        """
        Assert that two roman numerals of different value are not equal.
        """
        self.assertNotEqual(roman(1), roman(2))

    def test_roman_eq_int(self):
        """
        Assert that a roman numeral and decimal number
        of equal value are equal.
        """
        self.assertEqual(1, roman(1))

    def test_roman_ne_int(self):
        """
        Assert that a roman numeral and decimal number
        of different value are not equal.
        """
        self.assertNotEqual(2, roman(1))

    def test_roman_eq_str(self):
        """
        Assert that a roman numeral and a string representing
        a roman numeral of equal value are equal.
        """
        self.assertEqual("I", roman(1))

    def test_roman_ne_str(self):
        """
        Assert that a roman numeral and a string not representing
        a roman numeral of equal value are not equal.
        """
        self.assertNotEqual("II", roman(1))

    def test_roman_gt_roman(self):
        """
        Assert that a roman numeral is greater than
        another roman numeral of lesser value.
        """
        self.assertGreater(roman(2), roman(1))

    def test_roman_gt_int(self):
        """
        Assert that a roman numeral is greater than
        an integer of lesser value.
        """
        self.assertLess(roman(1), 2)

    def test_roman_lt_roman(self):
        """
        Assert that a roman numeral is lesser than
        another roman numeral of greater value.
        """
        self.assertLess(roman(1), roman(2))

    def test_roman_lt_int(self):
        """
        Assert that a roman numeral is lesser than
        an integer of greater value.
        """
        self.assertLess(roman(1), 2)

    def test_roman_ge_roman(self):
        """
        Assert that a roman numeral is greater than or equal to
        another roman numeral of lesser or equal value.
        """
        with self.subTest():
            self.assertGreaterEqual(roman(2), roman(1))
        with self.subTest():
            self.assertGreaterEqual(roman(1), roman(1))

    def test_roman_ge_int(self):
        """
        Assert that a roman numeral is greater than or equal to
        an integer of lesser or equal value.
        """
        with self.subTest():
            self.assertGreaterEqual(2, roman(1))
        with self.subTest():
            self.assertGreaterEqual(roman(1), roman(1))

    def test_roman_le_roman(self):
        """
        Assert that a roman numeral is less than or equal to
        another roman numeral of greater or equal value.
        """
        with self.subTest():
            self.assertLessEqual(1, roman(2))
        with self.subTest():
            self.assertLessEqual(roman(1), 1)
