"""
Definition of the RomanPy module.
"""
from typing import Union

_ENCODING_ASCII = "ascii"
_ENCODING_UNICODE = "unicode"

VARIANT_BASE = {
    1: "I",
    5: "V",
    10: "X",
    50: "L",
    100: "C",
    500: "D",
    1000: "M"
}

VARIANT_ZERO = {
    0: "N"
}

VARIANT_SUBTRACTIVE = {
    4: "IV",
    9: "IX",
    40: "XL",
    400: "CD",
    900: "CM"
}

VARIANT_SUBTRACTIVE_EXTENDED = {
    8: "IIX",
    17: "IIIXX",
    18: "IIXX",
    97: "IIIC",
    98: "IIC",
    99: "IC"
}

VARIANT_APOSTROPHUS = {
    500: "I)",
    1000: "(I)",
    5000: "I))",
    10000: "((I))",
    50000: "I)))",
    100000: "(((I)))"
}

VARIANT_MEDIEVAL = {
    5: "A",
    7: "Z",
    11: "O",
    40: "F",
    70: "S",
    80: "R",
    90: "N",
    150: "Y",
    151: "K",
    160: "T",
    200: "H",
    250: "E",
    300: "B",
    400: "P",
    500: "Q"
}

_MAPPING_UNICODE_UPPER = {
    "(((I)))": "ↈ",
    "I)))": "ↇ",
    "((I))": "ↂ",
    "I))": "ↁ",
    "(I)": "ↀ",
    "I)": "Ⅾ",
    "IX": "Ⅸ",
    "IV": "Ⅳ",
    "XII": "Ⅻ",
    "XI": "Ⅺ",
    "VIII": "Ⅷ",
    "VII": "Ⅶ",
    "VI": "Ⅵ",
    "III": "Ⅲ",
    "II": "Ⅱ",
    "M": "Ⅿ",
    "D": "Ⅾ",
    "C": "Ⅽ",
    "L": "Ⅼ",
    "X": "Ⅹ",
    "V": "Ⅴ",
    "I": "Ⅰ",
}

_MAPPING_UNICODE_LOWER = {
    ")": "ↄ",
    "(": "ⅽ",
    "IX": "ⅸ",
    "IV": "ⅳ",
    "XII": "ⅻ",
    "XI": "ⅺ",
    "VIII": "ⅷ",
    "VII": "ⅶ",
    "VI": "ⅵ",
    "III": "ⅲ",
    "II": "ⅱ",
    "M": "ⅿ",
    "D": "ⅾ",
    "C": "ⅽ",
    "L": "ⅼ",
    "X": "ⅹ",
    "V": "ⅴ",
    "I": "ⅰ"
}

_ENCODINGS = [
    _ENCODING_ASCII,
    _ENCODING_UNICODE,
]

_DEFAULT_ENCODING = _ENCODING_ASCII
_DEFAULT_VARIANT = VARIANT_BASE | VARIANT_SUBTRACTIVE


class _RomanNumeral(int):
    """
    The roman numeral class.
    """

    _encoding: str
    _uppercase: bool
    _variant: dict[int, str]

    def __new__(cls,
                value: Union[int, "_RomanNumeral"],
                encoding: str = None,
                uppercase: bool = None,
                variant: dict[int, str] = None):
        """
        Return an instance of a roman numeral with the specified properties.
        If the specified value is also a roman numeral, its properties will
        be used as a fallback for any properties that have not been specified.
        """
        if encoding is not None and encoding not in _ENCODINGS:
            raise ValueError(f"unknown encoding `{encoding}`")
        if value < 0:
            raise ValueError("a roman numeral cannot be negative")

        instance = super().__new__(cls, value)

        instance._encoding = encoding or getattr(value, "_encoding",
                                                 _DEFAULT_ENCODING)
        instance._uppercase = uppercase if uppercase is not None \
            else getattr(value, "_uppercase", True)
        instance._variant = variant or getattr(value, "_variant",
                                               _DEFAULT_VARIANT)

        return instance

    def encode(self, encoding: str):
        """
        Return a roman numeral of the same value and case as the current
        roman numeral, with the specified encoding.
        """
        return _RomanNumeral(self, encoding=encoding)

    def upper(self):
        """
        Return a roman numeral of the same value and encoding as the current
        roman numeral, in uppercase.
        """
        return _RomanNumeral(self, uppercase=True)

    def lower(self):
        """
        Return a roman numeral of the same value and encoding as the current
        roman numeral, in lowercase.
        """
        return _RomanNumeral(self, uppercase=False)

    def extend_variant(self, variant: dict[int, str]):
        """
        Return a roman numeral, identical to the current one, with current
        variant extended as specified.
        """
        return _RomanNumeral(self, variant=self._variant | variant)

    def set_variant(self, variant: dict[int, str]):
        """
        Return a roman numeral, identical to the current one, with the
        variant as specified.
        """
        return _RomanNumeral(self, variant=variant)

    def __str__(self):
        if int(self) == 0:
            return self._variant.get(0, "")

        carry = int(self)
        numeral = ""

        for value, digit in sorted(self._variant.items(), reverse=True):
            if value == 0:
                continue
            while value <= carry:
                carry = carry - value
                numeral = numeral + digit

        if self._encoding == _ENCODING_ASCII:
            return numeral if self._uppercase else numeral.lower()

        mapping = _MAPPING_UNICODE_UPPER if self._uppercase else \
            _MAPPING_UNICODE_LOWER

        for old, new in mapping.items():
            numeral = numeral.replace(old, new)

        return numeral

    def __repr__(self):
        return f"roman({int(self)})"

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self).upper() == other.upper()
        return super().__eq__(other)

    def __ne__(self, other):
        if isinstance(other, str):
            return str(self).upper() != other.upper()
        return super().__ne__(other)

    def _apply_operator(self, operator, other):
        """
        Helper method to apply the specified operator to the int superclass
        and wrap the result in a roman numeral with the same properties as
        the current one.

        :param operator: The operator to apply.
        :param other: The other roman numeral or int.
        """
        return _RomanNumeral(getattr(super(), operator)(other),
                             self._encoding,
                             self._uppercase,
                             self._variant)

    def __add__(self, other):
        return self._apply_operator("__add__", other)

    def __radd__(self, other):
        return self._apply_operator("__radd__", other)

    def __sub__(self, other):
        return self._apply_operator("__sub__", other)

    def __rsub__(self, other):
        return self._apply_operator("__rsub__", other)

    def __mul__(self, other):
        return self._apply_operator("__mul__", other)

    def __rmul__(self, other):
        return self._apply_operator("__rmul__", other)

    def __floordiv__(self, other):
        return self._apply_operator("__floordiv__", other)

    def __rfloordiv__(self, other):
        return self._apply_operator("__rfloordiv__", other)
