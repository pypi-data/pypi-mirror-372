# ruff: noqa: S101
import inspect
import json
import os

import pytest

from artemis_sg import items


@pytest.fixture()
def expected_no_scraped_data():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    isbn10a = "0802157009"
    isbn10b = "069102555X"
    description_a = ""
    description_b = ""
    image_urls = []
    sample_data = {
        isbn13a: {
            "isbn10": isbn10a,
            "DESCRIPTION": description_a,
            "image_urls": image_urls,
        },
        isbn13b: {
            "isbn10": isbn10b,
            "DESCRIPTION": description_b,
            "image_urls": image_urls,
        },
    }
    return sample_data


@pytest.fixture()
def items_collection_with_scraped_data(sample_item_list, sample_scraped_data):
    collection = items.Items(
        sample_item_list[0],
        sample_item_list[1:],
        "ISBN",
    )
    for item in collection:
        item.image_urls = sample_scraped_data[item.isbn]["image_urls"]
        item.data["DESCRIPTION"] = sample_scraped_data[item.isbn]["DESCRIPTION"]
        item.data["DIMENSION"] = sample_scraped_data[item.isbn]["DIMENSION"]
        item.data["RANKS"] = sample_scraped_data[item.isbn]["RANKS"]

    return collection


class TestItems:
    def test_create_items(self):
        """
        GIVEN Items class
        WHEN Items object is created
        THEN the object is of type items.Items
        AND the object contains items of type Item
        AND the object.isbn_key is set to the given key
        """
        collection = items.Items(["ISBN", "Foo_key"], [["val1", "val2"]], "ISBN")

        assert isinstance(collection, items.Items)
        assert isinstance(collection.items, list)
        assert isinstance(collection.items[0], items.Item)
        assert collection.isbn_key == "ISBN"

    def test_create_items_with_no_valid_data(self):
        """
        GIVEN item data that all evaluates to False
        WHEN Items object is created with that data
        THEN the items object contains zero items
        """
        collection = items.Items(["ISBN", "Foo_key"], [["", None]], "ISBN")

        assert isinstance(collection.items, list)
        assert len(collection.items) == 0

    def test_get_items(self):
        """
        GIVEN Items instance
        WHEN get_items method is called
        THEN the items list is returned
        """
        collection = items.Items(["ISBN", "Description"], [["val1", "val2"]], "ISBN")

        assert collection.get_items() == collection.items

    def test_find_item_with_tb_code(self):
        """
        GIVEN Items instance
        AND TBCODE is in the keys
        AND the isbn_key value is not valid
        WHEN items.find_item method is called
        AND the tb code is given as the input
        THEN it returns the correct item.
        """
        items_obj = items.Items(
            ["ISBN", "TBCODE"], [["invalid isbn", "tb code value"]], isbn_key="ISBN"
        )
        item = items_obj.find_item("tb code value")
        assert item == items_obj.get_items()[0]

    def test_iter(self):
        """
        GIVEN Items instance
        WHEN next method is called
        THEN first item in list is returned
        """
        collection = items.Items(["ISBN", "Description"], [["val1", "val2"]], "ISBN")

        for i in collection:
            assert i == collection.items[0]

    def test_update_collection_item_data(self, items_collection):
        """
        GIVEN a Items object with sample items
        WHEN we update a data element for the first item
        THEN the item data should not match the original item data
        AND the itme data of the unchanged item should match its original data
        """
        # select first item for updating
        for i, item in enumerate(items_collection):
            if i == 0:
                item_to_update = item
                data_to_update = item.data.copy()
            else:
                item_to_stay_the_same = item
                data_to_stay_the_same = item.data.copy()

        new_description = "New and improved version"
        item_to_update.data["DESCRIPTION"] = new_description

        assert item_to_update.data != data_to_update
        assert item_to_stay_the_same.data == data_to_stay_the_same

    def test_save__nothing_scraped_non_exiting_datafile(
        self, items_collection, target_directory
    ):
        """
        GIVEN a Items object with sample items with no scraped data
        WHEN when we call save_scraped_data() on the object
             with a datafile that doesn't exist
        THEN the datafile is not created
        """
        test_name = inspect.currentframe().f_code.co_name
        filename = os.path.join(target_directory, test_name + ".json")
        items_collection.save_scraped_data(filename)

        assert os.path.exists(filename) is False

    def test_save__nothing_scraped_empty_datafile(
        self, items_collection, empty_datafile
    ):
        """
        GIVEN a Items object with sample items with no scraped data
        AND an exitsting empty datafile
        WHEN when we call save_scraped_data() on the object with the datafile
        THEN the datafile should remain empty
        """
        items_collection.save_scraped_data(datafile=empty_datafile)
        with open(empty_datafile) as filepointer:
            empty_lines = filepointer.readlines()

        assert empty_lines == []

    def test_save__scraped_non_exiting_datafile(
        self,
        items_collection_with_scraped_data,
        expected_with_scraped_urls,
        target_directory,
    ):
        """
        GIVEN a Items object with sample items with scraped data
        WHEN when we call save_scraped_data() on the object
             with a datafile that doesn't exist
        THEN the datafile exists
        AND the datafile contains scraped data
        """
        test_name = inspect.currentframe().f_code.co_name
        filename = os.path.join(target_directory, test_name + ".json")
        items_collection_with_scraped_data.save_scraped_data(filename)

        assert os.path.exists(filename) is True
        with open(filename) as filepointer:
            data = json.load(filepointer)

        assert data == expected_with_scraped_urls

    def test_save__scraped_exiting_datafile(
        self,
        items_collection_with_scraped_data,
        expected_with_scraped_urls,
        unique_scraped_element,
        valid_datafile,
    ):
        """
        GIVEN a Items object with sample items with scraped data
        WHEN when we call save_scraped_data() on the object
             with a datafile that contains existing data
            * (new) in Items, but not in datafile
            * (updated) in both
            * (existing) in datafile, but not in Items
        THEN the datafile contains sample item 1
        AND the datafile sample item 2 has been updated
        AND the datafile contains its existing item unmodified
        """
        items_collection_with_scraped_data.save_scraped_data(valid_datafile)

        with open(valid_datafile) as filepointer:
            data = json.load(filepointer)

        new = "9780802157003"
        updated = "9780691025551"
        existing = "9780802150493"
        assert new in data
        assert updated in data
        assert existing in data
        assert data[new] == expected_with_scraped_urls[new]
        assert data[updated] == expected_with_scraped_urls[updated]
        assert data[existing] == unique_scraped_element[existing]

    def test_load_scraped_data(self, items_collection, valid_data, valid_datafile):
        """
        GIVEN saved json datafile with sample scraped data
        AND an Items object with sample items
        WHEN when we call load_scraped_data() on the object with the datafile
        THEN Items.item objects are updated with scraped data
        AND Items.item without scraped data remain empty
        AND no new items are created
        """
        item_isbns = [item.isbn for item in items_collection]
        data_isbns = list(valid_data)

        items_collection.load_scraped_data(datafile=valid_datafile)

        # Intersection of items should be updated
        for isbn in set(item_isbns) & set(data_isbns):
            item = items_collection.find_item(isbn)
            assert item
            assert item.isbn10 == valid_data[isbn]["isbn10"]
            assert item.image_urls == valid_data[isbn]["image_urls"]
            assert item.data["DESCRIPTION"] == valid_data[isbn]["DESCRIPTION"]

        # Difference of items should remain empty
        for isbn in set(item_isbns) - set(data_isbns):
            item = items_collection.find_item(isbn)
            assert item
            assert item.image_urls == []
            assert item.data["DESCRIPTION"] == ""

        # Difference of data elements should not exist in Items
        for isbn in set(data_isbns) - set(item_isbns):
            item = items_collection.find_item(isbn)
            assert item is None

    def test_load_no_file(self, items_collection):
        """
        GIVEN an Items object with sample items
        WHEN when we call load_scraped_data() on the object
             with a datafile that doesn't exist
        THEN the object's item image_urls attribute is empty
        AND the object's item data attribute is empty
        """
        items_collection.load_scraped_data(datafile="test_load_no_file")

        for item in items_collection:
            assert item.image_urls == []
            assert item.data["DESCRIPTION"] == ""

    def test_load_invalid_json(self, items_collection, empty_datafile):
        """
        GIVEN an Items object with sample items
        WHEN when we call load_scraped_data() on the object
            with a datafile that contains invalid json (i.e. empty)
        THEN the object's item image_urls attribute is empty
        AND the object's item data attribute is empty
        """
        items_collection.load_scraped_data(empty_datafile)

        for item in items_collection:
            assert item.image_urls == []
            assert item.data["DESCRIPTION"] == ""
