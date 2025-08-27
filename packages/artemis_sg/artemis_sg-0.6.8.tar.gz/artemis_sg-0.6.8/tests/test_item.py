# ruff: noqa: S101
import pytest

from artemis_sg import item
from artemis_sg.config import CFG

item_data = {
    "ISBN": "9780802157003",
    "PRICE": "$42",
    "DESCRIPTION": "cool description",
    "DIMENSION": "",
    "RANKS": {},
}
test_data = [
    (item_data, item_data),
    (item_data | {None: "foo"}, item_data),
    (item_data | {1234: "integer"}, item_data | {"1234": "integer"}),
]
test_ids = ["basic data", "data with None key", "data with non-string key"]


class TestItem:
    @pytest.mark.parametrize("data,expected_data", test_data, ids=test_ids)
    def test_create_item(self, data, expected_data):
        """
        GIVEN Item class
        WHEN Item instance is created
        THEN the instance is of type item.Item
        AND has a data attribute with the given values
        AND has an isbn attribute
        AND has an isbn10 attribute
        """
        isbn13 = "9780802157003"
        isbn10 = "0802157009"
        isbn_key = "ISBN"
        product = item.Item(
            list(data.keys()),
            list(data.values()),
            isbn_key,
        )

        assert isinstance(product, item.Item)
        assert product.data == expected_data
        assert product.isbn == isbn13
        assert product.isbn10 == isbn10
        assert product.image_urls == []

    def test_sort_order(self):
        """
        GIVEN an item object
        WHEN _sort_data is called on the item
        THEN the data is ordered in accordance with CFG preferences
        """
        isbn13 = "9780802157003"
        isbn_key = "ISBN"
        expected_data = {
            "ISBN": isbn13,
            "PRICE": "$42",
            "DESCRIPTION": "cool description",
            "DIMENSION": "",
            "AUTHOR": "Douglas Adams",
            "TITLE": "Hitchhiker's Guide to The Galaxy",
        }
        CFG["asg"]["item"]["sort_order"] = [
            "AUTHOR",
            "TITLE",
            "DIMENSION",
            "PRICE",
        ]
        ordered_keys = [
            "AUTHOR",
            "TITLE",
            "DIMENSION",
            "PRICE",
            "RANKS",
            "ISBN",
            "DESCRIPTION",
        ]

        product = item.Item(
            list(expected_data.keys()),
            list(expected_data.values()),
            isbn_key,
        )

        product._sort_data()
        assert isinstance(product, item.Item)
        assert list(product.data.keys()) == ordered_keys

    def test_invalid_isbn_with_tb_code(self):
        """
        GIVEN data dict with an invalid isbn value
        AND TBCODE is a key in the data
        WHEN an Item is created for the data
        THEN the Item.isbn is set to the TBCODE value

        """
        item_data = {
            "ISBN": "invalid",
            "PRICE": "$42",
            "DESCRIPTION": "cool description",
            "DIMENSION": "",
            "TBCODE": "2401362",
        }
        test_item = item.Item(item_data.keys(), item_data.values(), "ISBN")
        assert test_item.isbn == "2401362"
