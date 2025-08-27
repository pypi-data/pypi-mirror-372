import logging

import isbnlib

from artemis_sg.config import CFG
from artemis_sg.isbn import validate_isbn


class Item:
    """
    This class represents an Item object.

    Attributes:
    -----------
    data: dict
        Item data.
    data['DESCRIPTION']: str
        Item description.  Always created regardless of input `keys`.
    data['DIMENSION']: str
        Item dimension.  Always created regardless of input `keys`.
    isbn_key: str
        The key that should be used for associating isbn.
    isbn: str
        The ISBN-13 for the item.
    isbn10: str
        The ISBN-10 for the item.
    image_urls: list[str]
        Image URLs associated with the item.
    """

    def __init__(self, keys: list[str], values: list, isbn_key: str) -> None:
        """
        Constructs the necessary attributes for the item object

        :param keys:
            The keys used to build the item.data dictionary
        :param values: The values used to build the item.data dictionary
        :isbn_key:
            The key that should be used for associating isbn.
        """
        clean_keys = []
        for x in keys:
            if x:
                clean_keys.append(str(x).strip().upper())
        self.data = dict(zip(clean_keys, values))
        self.isbn_key = isbn_key
        if isbn_key:
            self.isbn = validate_isbn(self.data[isbn_key])
        else:
            self.isbn = ""
        if not self.isbn and self.data.get("TBCODE"):
            self.isbn = str(self.data.get("TBCODE"))
        self.isbn10 = isbnlib.to_isbn10(self.isbn)
        self.image_urls = []
        if "DESCRIPTION" not in self.data:
            self.data["DESCRIPTION"] = ""
        if "DIMENSION" not in self.data:
            self.data["DIMENSION"] = ""
        if "RANKS" not in self.data:
            self.data["RANKS"] = {}
        self._sort_data()

    def _sort_data(self):
        namespace = f"{type(self).__name__}.{self._sort_data.__name__}"

        def sort_order(e):
            defined_order = CFG["asg"]["item"]["sort_order"]
            if e in defined_order:
                return defined_order.index(e)
            return 99

        sorted_keys = list(self.data.keys())
        # sort by defined order
        sorted_keys.sort(key=sort_order)
        # move ISBN and DESCRIPTION to end of list
        sorted_keys.sort(key=self.isbn_key.__eq__)
        sorted_keys.sort(key="DESCRIPTION".__eq__)
        logging.debug(f"{namespace}: Sorted keys: {sorted_keys}")

        sorted_data = {key: self.data[key] for key in sorted_keys}
        self.data = sorted_data
