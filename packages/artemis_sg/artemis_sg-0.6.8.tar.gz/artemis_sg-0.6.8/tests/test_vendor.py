# ruff: noqa: S101
import pytest

from artemis_sg.vendor import vendor


@pytest.fixture
def vendor_data():
    return [
        {
            "code": "sample_defined_attrs",
            "name": "Super Sample Test Vendor",
            "isbn_key": "ISBN-13",
            "failover_scraper": "SuperScraper",
        },
        {
            "code": "sample_w_extra_attr",
            "name": "Another Test Vendor",
            "isbn_key": "ISBN",
            "failover_scraper": "KoolScraper",
            "extra_key": "myKey",
        },
        {
            "code": "sample_defined_attrs_mixed_case_isbn",
            "name": "Sample Test Vendor with mixed case isbn key",
            "isbn_key": "iSbN-13",
            "failover_scraper": "SuperScraper",
        },
    ]


def test_attributes_empty_data():
    """
    GIVEN a vendor code
    AND and empty vendor data set
    WHEN Vendor instance is created
    THEN the instances code attribute is set to the given code
    AND the instance has an empty all_data attribute
    AND the instance has an empty name attribute
    AND the instance has an empty isbn_key attribute
    AND the instance has an empty failover_scraper attribute
    """
    expected_attrs = {
        "code": "foo",
        "name": "",
        "isbn_key": "",
        "failover_scraper": "",
    }
    vendr = vendor(expected_attrs["code"], [{}])

    assert vendr.__dict__ == expected_attrs


def test_attributes_set_from_data(vendor_data):
    """
    GIVEN a vendor data set
    AND a vendor code in the data set
    AND the data is for defined Vendor attributes
    WHEN the vendor is created
    THEN the defined attributes are set
    """
    expected_attrs = vendor_data[0]  # sample_defined_attrs
    vendr = vendor(expected_attrs["code"], vendor_data)

    assert vendr.__dict__ == expected_attrs


def test_attributes_from_data_superset(vendor_data):
    """
    GIVEN a vendor data set
    AND a vendor code in the data set
    AND the data includes an 'extra_key' not defined in Vendor attributes
    WHEN the vendor is created
    THEN the defined attributes are set
    AND the 'extra_key' attribute is created
    """
    expected_attrs = vendor_data[1]  # sample_w_extra_attr
    vendr = vendor(expected_attrs["code"], vendor_data)

    assert vendr.__dict__ == expected_attrs


def test_isbn_key_attr_set_upper_case(vendor_data):
    expected_attrs_with_mixed_isbn = vendor_data[2]
    vendr = vendor(expected_attrs_with_mixed_isbn["code"], vendor_data.copy())
    assert vendr.isbn_key == expected_attrs_with_mixed_isbn["isbn_key"].upper()
