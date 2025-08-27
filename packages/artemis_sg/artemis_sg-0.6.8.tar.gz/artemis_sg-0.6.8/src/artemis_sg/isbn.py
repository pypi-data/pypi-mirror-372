import logging
import re
from os.path import basename, splitext

import isbnlib

MODULE = splitext(basename(__file__))[0]


def valid_sd_code(isbn: str) -> str:
    """
    Checks if isbn follows the internal Strathearn code pattern used for frames.
    >>> valid_sd_code('FI-6040')
    True
    >>> valid_sd_code('FI-604')
    False
    >>> valid_sd_code('US-6040')
    False
    """
    return bool(re.fullmatch(r"FI-\d{4}", isbn))


def validate_isbn(isbn: str) -> str:
    """
    Get validated ISBN-13 from given string

    :param isbn:
        String to be validated.
    :returns: A string of validated ISBN-13, or a 12-13 digit string,
    or an empty string if it cannot be validated.

    Example ISBN values:
    "ISBN-13"
    >>> validate_isbn("9780802150493")
    '9780802150493'

    "ISBN-10"
    >>> validate_isbn("0802157009")
    '9780802157003'

    "ISBN-10 with alpha"
    >>> validate_isbn("069102555X")
    '9780691025551'

    "ISBN-13 with added float"
    >>> validate_isbn("9780802150493.03")
    '9780802150493'

    "ISBN-10 with missing leading zero"
    >>> validate_isbn("123456789")
    '9780123456786'

    "ISBN-13 inside of formula string"
    >>> validate_isbn('="9780802150493"')
    '9780802150493'

    "Invalid ISBN"
    >>> validate_isbn("invalid")
    ''

    >>> validate_isbn("6696165018017")
    '6696165018017'

    "Not 12 or 13 digits and not valid ISBN-13 or ISBN-10 with leading 0's
    >>> validate_isbn("96165018017")
    ''

    >>> validate_isbn('FI-1738')
    'FI-1738'

    """
    namespace = f"{MODULE}.{validate_isbn.__name__}"
    valid_isbn = ""
    mod_isbn = str(isbn)
    if isbnlib.is_isbn13(mod_isbn) or isbnlib.is_isbn10(mod_isbn):
        valid_isbn = isbnlib.to_isbn13(mod_isbn)
    else:
        # look for formula value
        m = re.search('="(.*)"', mod_isbn)
        if m:
            mod_isbn = m.group(1)
        # look for float value
        mod_isbn = mod_isbn.split(".", 1)[0]
        if mod_isbn.isdigit() and len(mod_isbn) in (12, 13):
            if isbnlib.is_isbn13(mod_isbn) or isbnlib.is_isbn10(mod_isbn):
                valid_isbn = isbnlib.to_isbn13(mod_isbn)
            else:
                valid_isbn = mod_isbn
        elif valid_sd_code(mod_isbn):
            valid_isbn = mod_isbn
        else:
            # look for value with missing zero(s)
            mod_isbn = mod_isbn.zfill(10)
            if isbnlib.is_isbn13(mod_isbn) or isbnlib.is_isbn10(mod_isbn):
                valid_isbn = isbnlib.to_isbn13(mod_isbn)
            else:
                logging.error(f"{namespace}: Err reading isbn '{isbn}'")
    return valid_isbn
