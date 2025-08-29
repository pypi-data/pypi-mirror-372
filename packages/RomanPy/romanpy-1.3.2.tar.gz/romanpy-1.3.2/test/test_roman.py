"""
Tests for the Roman class.
"""
from unittest import TestCase

from roman import roman

TEST_ROMAN_NUMERALS_ASCII_UPPER = {
    39: "XXXIX",
    246: "CCXLVI",
    789: "DCCLXXXIX",
    2421: "MMCDXXI",
    160: "CLX",
    207: "CCVII",
    1009: "MIX",
    1066: "MLXVI",
    1776: "MDCCLXXVI",
    1918: "MCMXVIII",
    1954: "MCMLIV",
    2014: "MMXIV"
}

TEST_ROMAN_NUMERALS_ASCII_LOWER = {
    v: c.lower() for v, c in TEST_ROMAN_NUMERALS_ASCII_UPPER.items()
}

TEST_ROMAN_NUMERALS_UNICODE_UPPER = {
    39: "ⅩⅩⅩⅨ",
    246: "ⅭⅭⅩⅬⅥ",
    789: "ⅮⅭⅭⅬⅩⅩⅩⅨ",
    2421: "ⅯⅯⅭⅮⅩⅪ",
    160: "ⅭⅬⅩ",
    207: "ⅭⅭⅦ",
    1009: "ⅯⅨ",
    1066: "ⅯⅬⅩⅥ",
    1776: "ⅯⅮⅭⅭⅬⅩⅩⅥ",
    1918: "ⅯⅭⅯⅩⅧ",
    1954: "ⅯⅭⅯⅬⅣ",
    2014: "ⅯⅯⅩⅣ"
}

TEST_ROMAN_NUMERALS_UNICODE_LOWER = {
    39: "ⅹⅹⅹⅸ",
    246: "ⅽⅽⅹⅼⅵ",
    789: "ⅾⅽⅽⅼⅹⅹⅹⅸ",
    2421: "ⅿⅿⅽⅾⅹⅺ",
    160: "ⅽⅼⅹ",
    207: "ⅽⅽⅶ",
    1009: "ⅿⅸ",
    1066: "ⅿⅼⅹⅵ",
    1776: "ⅿⅾⅽⅽⅼⅹⅹⅵ",
    1918: "ⅿⅽⅿⅹⅷ",
    1954: "ⅿⅽⅿⅼⅳ",
    2014: "ⅿⅿⅹⅳ"
}


class TestRoman(TestCase):
    """
    A test case for the Roman class.
    """

    def test_roman_int_to_ascii_upper(self):
        """
        Assert that a decimal number can be converted to
        an ASCII upper-case roman numeral.
        """
        for value, numeral in TEST_ROMAN_NUMERALS_ASCII_UPPER.items():
            with self.subTest(value=value):
                self.assertEqual(numeral, str(roman(value)))

    def test_roman_int_to_ascii_lower(self):
        """
        Assert that a decimal number can be converted to
        an ASCII lower-case roman numeral.
        """
        for value, numeral in TEST_ROMAN_NUMERALS_ASCII_LOWER.items():
            with self.subTest(value=value):
                self.assertEqual(numeral, str(roman(value).lower()))

    def test_roman_int_to_unicode(self):
        """
        Assert that a decimal number can be converted to
        a unicode roman numeral.
        """
        for value, numeral in TEST_ROMAN_NUMERALS_UNICODE_UPPER.items():
            with self.subTest(value=value):
                self.assertEqual(numeral, str(roman(value).encode("unicode")))

    def test_roman_int_to_unicode_lower(self):
        """
        Assert that a decimal number can be converted to
        a unicode lower-case roman numeral.
        """
        for value, numeral in TEST_ROMAN_NUMERALS_UNICODE_LOWER.items():
            with self.subTest(value=value):
                self.assertEqual(
                    numeral, str(roman(value).encode("unicode").lower()))
