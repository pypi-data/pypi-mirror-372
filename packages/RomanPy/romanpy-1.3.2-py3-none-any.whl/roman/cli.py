#! /usr/bin/env python3

"""
Provide a CLI for generating roman numerals from the command-line.
"""

import os
import re
from argparse import ArgumentParser
from importlib import metadata

import tomli

from .roman import (_RomanNumeral, _ENCODING_ASCII, _ENCODING_UNICODE,
                    VARIANT_BASE, VARIANT_SUBTRACTIVE,
                    VARIANT_SUBTRACTIVE_EXTENDED, VARIANT_APOSTROPHUS,
                    VARIANT_MEDIEVAL, VARIANT_ZERO)


def _verbose_print(current: int, required: int, message: str):
    """
    Print the specified message if the current verbosity leve is equal to or
    greater than the required verbosity level.

    :param current: The current verbosity level.
    :param required: The required verbosity level.
    :param message: The message to print.
    """
    if current < required:
        return
    print(message)


def _version() -> str:
    """
    Provide the current version of RomanPy.

    :return: The current version of RomanPy.
    """
    try:
        return metadata.version("RomanPy")
    except metadata.PackageNotFoundError:
        pass

    path = os.path.join(os.path.dirname(__file__), "pyproject.toml")
    with open(path, "rb") as file:
        toml = tomli.load(file)
    assert ("project" in toml and "version" in toml["project"]), \
        "missing version in pyproject.toml"
    return toml["project"]["version"]


def main():
    """
    Provide a CLI for converting decimal numbers to Roman numerals.
    """

    parser = ArgumentParser(prog="roman",
                            description="Convert a decimal number to roman "
                                        "numeral.")

    encoding_group = parser.add_mutually_exclusive_group()
    encoding_group.add_argument("-a", "--ascii",
                                action="store_true",
                                help="output encoding of roman numerals in "
                                     "lowercase ascii")
    encoding_group.add_argument("-A", "--ASCII",
                                action="store_true",
                                help="output encoding of roman numerals in "
                                     "uppercase ascii (default)")
    encoding_group.add_argument("-u", "--unicode",
                                action="store_true",
                                help="output encoding of roman numerals in "
                                     "lowercase unicode")
    encoding_group.add_argument("-U", "--UNICODE",
                                action="store_true",
                                help="output encoding of roman numerals in "
                                     "uppercase unicode")

    variant_base_group = parser.add_mutually_exclusive_group()

    variant_base_group.add_argument("-b", "--no-base",
                                    action="store_true",
                                    help="do not use the base variant")

    variant_base_group.add_argument("-s", "--subtractive",
                                    action="store_true",
                                    help="use the subtractive variant "
                                         "(includes base) (default)")

    variant_base_group.add_argument("-e", "--subtractive-extended",
                                    action="store_true",
                                    help="use the extended subtractive variant"
                                         "(includes subtractive)")

    parser.add_argument("-z", "--zero",
                        action="store_true",
                        help="use the zero variant N")

    parser.add_argument("-p", "--apostrophus",
                        action="store_true",
                        help="use the apostrophus method for large numbers")

    parser.add_argument("-m", "--medieval",
                        action="store_true",
                        help="use the medieval variant")

    parser.add_argument("-c", "--custom",
                        nargs=2,
                        action="append",
                        metavar=("DECIMAL", "NUMERAL"),
                        help="map a decimal number to a roman numeral")

    parser.add_argument("-v", "--verbose",
                        action="count",
                        default=0,
                        help="increase verbosity")

    parser.add_argument("-V", "--version",
                        action="version",
                        version=_version())

    parser.add_argument("value",
                        help="a decimal number to convert to a roman numeral")

    args = parser.parse_args()

    _verbose_print(args.verbose, 1, f"verbosity {args.verbose}")

    if not re.fullmatch(r"\d+", args.value):
        parser.error("value must be an integer")

    args.ASCII = not args.ascii and not args.unicode and not args.UNICODE

    _verbose_print(args.verbose, 1,
                   "ascii mode" if args.ASCII else "unicode mode")

    uppercase = args.ASCII or args.UNICODE

    _verbose_print(args.verbose, 1,
                   "uppercase mode" if uppercase else "lowercase mode")

    if args.ascii or args.ASCII:
        encoding = _ENCODING_ASCII
    else:
        encoding = _ENCODING_UNICODE

    variant = {}

    subtractive = args.subtractive or (not args.no_base and not args.subtractive_extended)

    if not args.no_base:
        variant = variant | VARIANT_BASE
    if subtractive:
        variant = variant | VARIANT_SUBTRACTIVE
    if args.subtractive_extended:
        variant = variant | VARIANT_SUBTRACTIVE_EXTENDED
    if args.zero:
        variant = variant | VARIANT_ZERO
    if args.apostrophus:
        variant = variant | VARIANT_APOSTROPHUS
    if args.medieval:
        variant = variant | VARIANT_MEDIEVAL

    if args.custom:
        for decimal, numeral in args.custom:
            variant[int(decimal)] = numeral
            _verbose_print(args.verbose, 1,
                           f"custom numeral {numeral} ({decimal})")

    _verbose_print(args.verbose, 2,
                   "\n".join(f"{d} = {n}" for d, n in variant.items()))

    return _RomanNumeral(int(args.value),
                         encoding=encoding,
                         uppercase=uppercase,
                         variant=variant)


if __name__ == "__main__":
    print(main())
