# ruff: noqa: S101
import json
import logging
import os
import pathlib
from unittest.mock import Mock, patch

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from artemis_sg import scraper


@pytest.fixture(scope="session")
def driver(request):
    _driver = scraper.get_driver("--no-sandbox")
    yield _driver
    _driver.close()


@pytest.fixture()
def wave_scraper(driver, waveserver):
    yield scraper.WaveScraper(driver, base_url=waveserver, timeout=1, login_timeout=10)


def test_get_driver(monkeypatch):
    """
    GIVEN a webdriver object
    WHEN `get_driver` is called
    THEN a `Chrome` is called on the webdriver object
    AND a chrome driver is returned
    """
    driver = Mock(name="mock_driver")
    chrome = Mock(name="mock_chrome")
    driver.Chrome.return_value = chrome
    driver.execute_script.return_value = "foo"
    chrome.execute_script.return_value = "foo"
    monkeypatch.setattr(scraper, "webdriver", driver)

    d = scraper.get_driver()

    assert d == chrome


def test_main(monkeypatch, valid_datafile):
    """
    GIVEN a webdriver object
    WHEN `get_driver` is called
    THEN a `Chrome` is called on the webdriver object
    AND a chrome driver is returned
    """
    spreadsheet = Mock(name="mock_spreadsheet")
    spreadsheet.get_sheet_data.return_value = [["ISBN"], ["1234"]]
    monkeypatch.setattr(scraper, "spreadsheet", spreadsheet)
    driver = Mock(name="mock_driver")
    scrapr = Mock(name="mock_scraper")
    scrapr.scrape_description.return_value = "Be excellent to each other."
    scrapr.scrape_dimension.return_value = "Bigger on the inside."
    scrapr.scrape_item_image_urls.return_value = ["Bill", "Ted"]
    monkeypatch.setattr(scraper, "get_driver", lambda *args: driver)
    monkeypatch.setattr(scraper, "AmznScraper", lambda *args: scrapr)

    scraper.main(
        "foo",
        "my_workbook",
        "worksheet",
        valid_datafile,
        update_images_flag=None,
        update_ranks_flag=False,
    )

    driver.quit.assert_called  # noqa: B018


class TestBaseScraper:
    def test_create_scraper(self):
        """
        GIVEN BaseScraper class
        WHEN we create Scraper object with driver and url
        THEN object's selenium_driver and base_url attributes
             are set to the given values
        """
        scrapr = scraper.BaseScraper("driver", "baseUrl")

        assert scrapr.selenium_driver == "driver"
        assert scrapr.base_url == "baseUrl"

    def test_create_scraper_no_baseurl(self):
        """
        GIVEN BaseScraper class
        WHEN we create Scraper object with driver and no url
        THEN object's selenium_driver is set to the given value
        AND the base_url is set to an empty string
        """
        scrapr = scraper.BaseScraper("driver")

        assert scrapr.selenium_driver == "driver"
        assert scrapr.base_url == ""

    def test_load_item_page(self):
        """
        GIVEN BaseScraper object
        WHEN load_item_page is called on it with an item number
        THEN False is returned
        """
        scrapr = scraper.BaseScraper("driver")

        assert scrapr.load_item_page("1234") is False

    def test_scrape_description(self):
        """
        GIVEN BaseScraper object
        WHEN scrape_description is called on it
        THEN an empty string is returned
        """
        scrapr = scraper.BaseScraper("driver")

        assert scrapr.scrape_description() == ""

    def test_scrape_dimension(self):
        """
        GIVEN BaseScraper object
        WHEN scrape_dimension is called on it
        THEN an empty string is returned
        """
        scrapr = scraper.BaseScraper("driver")

        assert scrapr.scrape_dimension() == ""

    def test_scrape_item_image_urls(self):
        """
        GIVEN BaseScraper object
        WHEN scrape_item_image_urls is called on it
        THEN an empty list is returned
        """
        scrapr = scraper.BaseScraper("driver")

        assert scrapr.scrape_item_image_urls() == []

    def test_delay(self, monkeypatch):
        """
        GIVEN BaseScraper object
        WHEN delay is called on it
        THEN time.sleep is called
        """
        mock = Mock()
        scrapr = scraper.BaseScraper("driver")
        monkeypatch.setattr(scraper, "time", mock)

        scrapr.delay(42)
        mock.sleep.assert_called_with(42)


class TestAmznUkScraper:
    @pytest.mark.integration()
    def test_load_item_page(self):
        """
        GIVEN an ISBN only available in UK
        WHEN load_item_page is executed
        THEN true is returned
        """
        driver = scraper.get_driver()
        scrapr = scraper.AmznUkScraper(driver)
        scrapr.load_item_page("9780241605783")
        urls = scrapr.scrape_item_image_urls()
        driver.close()

        assert isinstance(urls, list)
        assert len(urls) > 0
        assert "https://m.media-amazon.com/images" in urls[0]


class TestAmznScraper:
    def test_scrape_description_with_review(self, monkeypatch):
        """
        GIVEN a AmznScraper object with webdriver and amazon url
        AND Amazon item page with editorial review is loaded in browser
        WHEN we call scrape_description() on object
        THEN the result is the editorial review without the first two lines
        """
        review_text = """Editorial Reviews
Review
Praise for Earthlings:
A New York Times Book Review Editors’ Choice
Named a Best Book of the Year by TIME and Literary Hub
Named a Most Anticipated Book by the New York Times, TIME, USA Today, \
Entertainment Weekly, the Guardian, Vulture, Wired, Literary Hub, Bustle, \
Popsugar, and Refinery29
“To Sayaka Murata, nonconformity is a slippery slope . . . Reminiscent of certain \
excellent folk tales, expressionless prose is Murata’s trademark . . . \
In Earthlings, being an alien is a simple proxy for being alienated. The characters \
define themselves not by a specific notion of what they are—other—but by a general \
idea of what they are not: humans/breeders . . . The strength of [Murata’s] voice \
lies in the faux-naïf lens through which she filters her dark view of humankind: \
We earthlings are sad, truncated bots, shuffling through the world in a dream of \
confusion.”—Lydia Millet, New York Times Book Review"""  # noqa: RUF001

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=review_text)
        driver.find_element.return_value = elem
        scrapr = scraper.AmznScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        expected_text = review_text.splitlines()
        expected_text.pop(0)
        expected_text.pop(0)
        expected_text = "\n".join(expected_text)
        assert description == expected_text

    def test_scrape_description_without_review(self, monkeypatch):
        """
        GIVEN Amazon item page without editorial review is loaded
        WHEN scrape_description is executed
        THEN description is returned
        """

        whole_description = (
            "As a child, Natsuki doesn’t fit into her family. "  # noqa: RUF001
            "Her parents favor her sister, and her best friend "
            "is a plush toy hedgehog named Piyyut who has "
            "explained to her that he has come from the planet "
            "Popinpobopia on a special quest to help her save "
            "the Earth."
        )

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=whole_description)
        driver.find_element.side_effect = [
            NoSuchElementException,
            elem,
        ]
        scrapr = scraper.AmznScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert "As a child" in description

    def test_scrape_dimension(self, monkeypatch):
        """
        GIVEN Amazon item page
        WHEN scrape_dimension is executed
        THEN the dimension is returned
        """
        dimension = "1.0 x 1.0 x 1.0 inches"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        elem.get_attribute.return_value = dimension
        driver.find_element.side_effect = [
            elem,
        ]
        scrapr = scraper.AmznScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver

        scrapr.load_item_page("item_number")

        assert scrapr.scrape_dimension() == dimension

    @pytest.mark.parametrize("method_", ["scrape_description", "scrape_dimension"])
    def test_nosuch_element(self, method_):
        """
        GIVEN NoSuchEelement on page
        WHEN {method_} is called on it
        THEN an empty string is returned
        """
        driver = Mock(name="mock_driver")
        driver.find_element.side_effect = [
            NoSuchElementException,
            NoSuchElementException,
        ]
        scrapr = scraper.AmznScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver

        assert getattr(scrapr, method_)() == ""

    def test_scrape_item_image_urls(self, driver, amazon_item_url):
        """
        GIVEN Amazon item page with multiple item images
        WHEN scrape_item_image_urls is executed
        THEN a list of urls is returned
        """
        scrapr = scraper.AmznScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        scrapr.selenium_driver.get(amazon_item_url)
        urls = scrapr.scrape_item_image_urls()

        assert isinstance(urls, list)
        assert "https://m.media-amazon.com/images/I/41znl9tN4xL.jpg" in urls[0]

    def test_scrape_rank(self, driver, amazon_item_url):
        scrapr = scraper.AmznScraper(driver)
        scrapr.selenium_driver = driver
        scrapr.selenium_driver.get(amazon_item_url)
        expected_rank = "376,058"
        rank = scrapr.scrape_rank()
        assert rank == expected_rank

    def test_get_span_type_thumb_id_prefix_no_imgThumbs_no_imgTagWrapperID(  # noqa: N802
        self, monkeypatch, caplog
    ):
        """
        GIVEN AmznScraper object
        WHEN get_span_type_thumb_id_prefix is executed
        AND no "imgThumbs" are found
        AND no "imgTagWrapperID" are found
        THEN (None, None) is returned
        AND log messages are emitted
        """
        caplog.set_level(logging.INFO)
        driver = Mock(name="mock_driver")
        driver.find_element.side_effect = scraper.NoSuchElementException("Boom!")
        scrapr = scraper.AmznScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "timeout", 0)
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.get_span_type_thumb_id_prefix()

        assert res == (None, None)
        assert (
            "root",
            logging.INFO,
            (
                "AmznScraper.get_span_type_thumb_id_prefix: "
                "No imgThumbs id, trying imgTagWrapperID"
            ),
        ) in caplog.record_tuples
        assert (
            "root",
            logging.INFO,
            "AmznScraper.get_span_type_thumb_id_prefix: No imgTagWrapperId id",
        ) in caplog.record_tuples


class TestTBScraper:
    def test_scrape_description(self, monkeypatch):
        """
        GIVEN TB item page
        WHEN scrape_description is executed
        THEN description is returned
        AND 'NO AMAZON SALES' has been removed from it
        """
        whole_description = """NO AMAZON SALES

Discover the mystery and power of the natural and human worlds in this \
beautifully illustrated coloring book.

Featuring tarot cards, healing herbs and flowers, mandalas, and curious \
creatures of the night, Believe in Magic is a spellbinding celebration \
of modern witchcraft with a focus on healing, mindfulness, and meditation."""

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=whole_description)
        driver.find_element.return_value = elem
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert "NO AMAZON SALES" not in description
        assert description.startswith("Discover the mystery")

    def test_scrape_dimension(self):
        """
        GIVEN TB item page
        WHEN scrape_dimension is executed
        THEN the dimension is returned
        """
        dimension = "Size: 1.0 x 1.0 x 1.0 inches\n"
        expected_dimension = "1.0 x 1.0 x 1.0 inches"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=dimension)
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
        ]
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver

        scrapr.load_item_page("item_number")

        assert scrapr.scrape_dimension() == expected_dimension

    @pytest.mark.parametrize("method_", ["scrape_description", "scrape_dimension"])
    def test_nosuch_element(self, method_):
        """
        GIVEN NoSuchEelement on page
        WHEN {method_} is called on it
        THEN an empty string is returned
        """
        driver = Mock(name="mock_driver")
        driver.find_element.side_effect = [
            NoSuchElementException,
            NoSuchElementException,
        ]
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver

        assert getattr(scrapr, method_)() == ""

    def test_scrape_item_image_urls(self, driver, tb_item_url, data_path):
        """
        GIVEN TB item page
        WHEN scrape_item_image_urls is executed
        THEN a URL list is returned
        AND the list contains the expected URL
        """
        full_path = os.path.join(
            data_path,
            "tb",
            "tb_files",
            "0043894_a-portrait-of-the-artist-as-a-young-man-arc-classic.jpeg",
        )
        expected_url = pathlib.Path(full_path).as_uri()

        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver

        scrapr.selenium_driver.get(tb_item_url)
        urls = scrapr.scrape_item_image_urls()

        assert len(urls) > 0
        assert expected_url in urls

    def test_login(self, capsys, monkeypatch):
        """
        GIVEN TB login page is loaded
        WHEN `login` is executed
        THEN user input message is displayed
        """
        expected_output = "USER INPUT REQUIRED"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.return_value = elem
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        scrapr.login()
        captured = capsys.readouterr()
        assert expected_output in captured.out

    def test_impersonate(self, monkeypatch):
        """
        GIVEN TBScraper instance
        WHEN `impersonate` is executed with a given valid email
        THEN the result is True
        AND the email has been searched for via the 'customers-grid' XPATH
        """
        email = "foo@example.org"
        email_xpath = (
            f"//div[@id='customers-grid']/table/tbody/tr/td/a[text()='{email}']"
        )

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem]

        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.impersonate(email)

        assert res is True
        driver.find_element.assert_any_call("xpath", email_xpath)

    def test_impersonate_multiple_customer_records(self, caplog, monkeypatch):
        """
        GIVEN TBScraper instance
        AND an email associated with multiple customer records
        WHEN `impersonate` is executed with that email
        THEN an exception is thrown
        """
        email = "foo@example.org"
        email_xpath = (
            f"//div[@id='customers-grid']/table/tbody/tr/td/a[text()='{email}']"
        )

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem]

        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        try:
            res = scrapr.impersonate(email)
            driver.find_element.assert_any_call("xpath", email_xpath)
            assert res is True
        except Exception:
            assert (
                "root",
                logging.ERROR,
                (
                    "TBScraper.impersonate: Found multiple customer records for "
                    f"email '{email}' to impersonate"
                ),
            ) in caplog.record_tuples

    def test_add_to_cart(self, monkeypatch):
        """
        GIVEN TB item page
        WHEN add_to_cart is executed with a given quantity
        THEN the cart contains the given quantity of the item
        """
        qty = "42"
        available = "999"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=f"Availability: {available} in stock")
        driver.find_element.return_value = elem
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.add_to_cart(qty)

        assert res == int(qty)

    def test_add_to_cart_adjust_qty(self, monkeypatch):
        """
        GIVEN TB item page
        WHEN add_to_cart is executed with a given quantity
             that is greater than available
        THEN the available quantity is returned
        """
        qty = "42"
        available = "10"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=f"Availability: {available} in stock")
        driver.find_element.return_value = elem
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.add_to_cart(qty)

        assert res == int(available)

    def test_load_cart_page(self, monkeypatch):
        """
        GIVEN an TBScraper object
        WHEN `load_cart_page` is executed on that object
        THEN the result is True
        """
        driver = Mock(name="mock_driver")
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.load_cart_page()

        assert res

    def test_search_item_num(self, monkeypatch):
        """
        GIVEN an TBScraper object
        WHEN `search_item_num` is executed on that object
        THEN the item number associated with elements href value is returned
        """
        driver = Mock(name="mock_driver")
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        elem = Mock(name="mock_elem")
        elem.get_attribute.return_value = "/p/123456789/hello-uk-world"
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem, elem]
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.search_item_num("foo")

        assert res == "123456789"

    def test_search_item_num_uk(self, monkeypatch):
        """
        GIVEN an TBScraper object
        WHEN `search_item_num` is executed on that object
        AND the string value of the href for that item begins with 'uk-'
        THEN the expected item number is NOT returned
        """
        driver = Mock(name="mock_driver")
        scrapr = scraper.TBScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        elem = Mock(name="mock_elem")
        elem.get_attribute.return_value = "/p/123456789/uk-do-not-find-ma"
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem, elem]
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.search_item_num("foo")

        assert res == ""


class TestSDScraper:
    def test_scrape_description(self, monkeypatch):
        """
        GIVEN SD item page
        WHEN scrape_description is executed
        THEN description is returned
        """
        expected_description = "Hello, World!"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=expected_description)
        driver.find_element.return_value = elem
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert description == expected_description

    def test_scrape_dimension(self, monkeypatch):
        """
        GIVEN SD item page
        WHEN scrape_dimension is executed
        THEN the dimension is returned
        """
        dimension = "Physical Dimensions:\n1.0 x 1.0 x 1.0 inches"
        expected_dimension = "1.0 x 1.0 x 1.0 inches"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=dimension)
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
            elem,
            elem,
        ]
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")

        assert scrapr.scrape_dimension() == expected_dimension

    @pytest.mark.parametrize("method_", ["scrape_description", "scrape_dimension"])
    def test_nosuch_element(self, method_):
        """
        GIVEN NoSuchEelement on page
        WHEN {method_} is called on it
        THEN an empty string is returned
        """
        driver = Mock(name="mock_driver")
        driver.find_element.side_effect = [
            NoSuchElementException,
            NoSuchElementException,
        ]
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver

        assert getattr(scrapr, method_)() == ""

    def test_scrape_item_image_urls(self, monkeypatch):
        """
        GIVEN SD item page
        WHEN scrape_item_image_urls is executed
        THEN a URL list is returned
        AND the list contains the expected URL
        """

        url = "http://example.org/foo/bar.jpg"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem, elem]
        elem.get_attribute.return_value = url
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        urls = scrapr.scrape_item_image_urls()
        assert len(urls) > 0
        assert url in urls

    def test_login(self, capsys, monkeypatch):
        """
        GIVEN SD login page is loaded
        WHEN `login` is executed
        THEN user input message is displayed
        """
        expected_output = "USER INPUT REQUIRED"

        driver = Mock(name="mock_driver")
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        scrapr.login()
        captured = capsys.readouterr()
        assert expected_output in captured.out

    def test_add_to_cart(self, monkeypatch):
        """
        GIVEN SD item page
        AND user is logged into SD
        WHEN add_to_cart is executed with a given quantity
        THEN the given quantity is returned
        """
        qty = "42"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text="Add to cart")
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem, elem]
        elem.get_attribute.return_value = "foo"
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        res = scrapr.add_to_cart(qty)

        assert res == int(qty)

    def test_add_to_cart_adjust_qty(self, monkeypatch):
        """
        GIVEN SD item page
        AND user is logged into SD
        WHEN add_to_cart is executed with a given quantity
             that is greater than available
        THEN the available quantity is returned
        """
        qty = "42"
        available = 10

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text="Add to cart")
        driver.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem]
        elem.find_element.return_value = elem
        elem.get_attribute.return_value = f"{available} in stock"
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        res = scrapr.add_to_cart(qty)

        assert res == available

    def test_load_cart_page(self, monkeypatch):
        """
        GIVEN an SDScraper object
        WHEN `load_cart_page` is executed on that object
        THEN the result is True
        """
        driver = Mock(name="mock_driver")
        scrapr = scraper.SDScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.load_cart_page()

        assert res


class TestGJScraper:
    def test_scrape_description(self, monkeypatch):
        """
        GIVEN GJ item page
        WHEN scrape_description is executed
        THEN description is returned
        """
        expected_description = "Hello, World!"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=expected_description)
        driver.find_element.return_value = elem
        elem.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem]
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert description == expected_description

    def test_scrape_description_fail(self, monkeypatch):
        """
        GIVEN GJ item page
        WHEN scrape_description is executed
        AND an exception is thrown
        THEN an empty string is returned
        """
        expected_description = ""

        driver = Mock(name="mock_driver")
        driver.find_element.side_effect = NoSuchElementException
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        scrapr.timeout = 0
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        description = scrapr.scrape_description()

        assert description == expected_description

    def test_scrape_item_image_urls(self, monkeypatch):
        """
        GIVEN GJ item page
        WHEN scrape_item_image_urls is executed
        THEN a URL list is returned
        AND the list contains the expected URL
        """

        url = "http://example.org/foo/bar.jpg"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text="foo")

        driver.find_element.return_value = elem
        elem.find_element.return_value = elem
        driver.find_elements.return_value = [elem, elem]
        elem.get_attribute.return_value = url
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_item_page("item_number")
        urls = scrapr.scrape_item_image_urls()

        assert len(urls) > 0
        assert url in urls

    def test_login(self, capsys, monkeypatch):
        """
        GIVEN GJ login page
        WHEN login is executed
        THEN user input message is displayed
        """
        expected_output = "USER INPUT REQUIRED"

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem")
        driver.find_element.return_value = elem
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        scrapr.login()
        captured = capsys.readouterr()
        assert expected_output in captured.out

    def test_add_to_cart(self, monkeypatch):
        """
        GIVEN GJ item page
        AND user is logged into GJ
        WHEN add_to_cart is executed with a given quantity
        THEN the cart contains the given quantity of the item
        """
        qty = "42"
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text="foo")

        driver.find_element.return_value = elem
        elem.find_element.return_value = elem
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        res = scrapr.add_to_cart(qty)

        assert res == int(qty)

    def test_add_to_cart_adjust_qty(self, monkeypatch):
        """
        GIVEN GJ item page
        AND user is logged into GJ
        WHEN add_to_cart is executed with a given quantity
             that is greater than available
        THEN the cart contains the available quantity of the item
        """
        qty = "42"
        available = 10

        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text=f"{available} in stock")
        driver.find_element.return_value = elem
        elem.find_element.return_value = elem
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        scrapr.load_login_page()

        res = scrapr.add_to_cart(qty)

        assert res == available

    def test_load_cart_page(self, monkeypatch):
        """
        GIVEN an GJScraper object
        WHEN `load_cart_page` is executed on that object
        THEN the result is True
        """
        driver = Mock(name="mock_driver")
        scrapr = scraper.GJScraper(driver)
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.load_cart_page()

        assert res

    def test_scrape_error_msg(self, monkeypatch):
        """
        GIVEN GJScraper instance
        WHEN scrape_error_mgs is executed
        THEN the expected message is returned
        """
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text="foo")

        driver.find_element.return_value = elem
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        result = scrapr.scrape_error_msg()

        assert result == "foo"

    def test_load_item_page_failed_account(self, monkeypatch):
        """
        GIVEN an GJScraper object
        WHEN `load_item_page` is executed on that object
        AND the "Account Summary" is not available
        THEN the result is True
        """
        driver = Mock(name="mock_driver")
        driver.find_element.side_effect = NoSuchElementException
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "timeout", 0)
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.load_item_page("1234")

        assert res is True

    def test_load_item_page_no_results(self, monkeypatch):
        """
        GIVEN an GJScraper object
        WHEN `load_item_page` is executed on that object
        AND the "No Results" are found
        THEN the result is False
        """
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem", text="No Results")
        driver.find_element.return_value = elem
        elem.find_element.return_value = elem
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "timeout", 0)
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        res = scrapr.load_item_page("1234")

        assert res is False

    def test_load_item_page_failed_with_account(self, monkeypatch, caplog):
        """
        GIVEN an GJScraper object
        WHEN `load_item_page` is executed on that object
        AND the "Accout Summary" is found
        AND search throws an exception
        THEN the result is False
        AND a failed message is logged
        """
        caplog.set_level(logging.INFO)
        driver = Mock(name="mock_driver")
        elem = Mock(name="mock_elem_acct", text="Account Summary")
        driver.find_element.side_effect = [
            elem,
            elem,
            elem,
            elem,
            NoSuchElementException,
        ]
        scrapr = scraper.GJScraper(driver)
        # hack in driver to ensure that Singleton bleed doesn't spoil test
        scrapr.selenium_driver = driver
        monkeypatch.setattr(scrapr, "timeout", 0)
        monkeypatch.setattr(scrapr, "delay", lambda *args: None)

        item_number = "1234"
        res = scrapr.load_item_page(item_number)

        assert res is False
        assert (
            "root",
            logging.INFO,
            f"GJScraper.load_item_page: failed item search for {item_number}",
        ) in caplog.record_tuples


class TestWaveScraper:
    ISBN = "9781684126590"

    def test_load_login_page(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        WHEN load_login_page is called
        THEN the login page is loaded
        """
        wave_scraper.load_login_page()
        assert wave_scraper.selenium_driver.find_element(By.CLASS_NAME, "login-form")

    @pytest.mark.integration("Requires manual credential entry")
    def test_login(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        AND we are not logged in
        WHEN login is called
        AND user credentials are entered
        THEN the user is logged in
        """
        wave_scraper.loggedin = False
        wave_scraper.login()
        assert wave_scraper.selenium_driver.find_element(By.CLASS_NAME, "btn-log-out")
        assert wave_scraper.loggedin

    def test_item_search(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        WHEN item_search is called with an ISBN
        THEN the search result page is loaded
        AND the results contain a link to the product page of the ISBN
        """
        url = wave_scraper.item_search(self.ISBN)
        assert url == "http://localhost:22222/products/view/4636"

    def test_item_search_no_match_found(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        WHEN item_search is called with an ISBN not in the database
        THEN the search result page is loaded
        AND the results do not contain a link to the product page of the ISBN
        """
        unknown_isbn = "9780802150578"
        url = wave_scraper.item_search(unknown_isbn)
        assert not url

    def test_load_item_page(self, driver, wave_scraper):
        """
        GIVEN a WaveScraper object
        AND we are logged in
        WHEN load_item_page is called with an ISBN
        THEN the product page for that ISBN is loaded
        """
        wave_scraper.loggedin = True
        wave_scraper.load_item_page(self.ISBN)
        item_code_text = wave_scraper.selenium_driver.find_element(
            By.CLASS_NAME, "product-info_item.code"
        ).text
        assert self.ISBN in item_code_text

    def test_scrape_description(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        AND a product item page
        AND we are logged in
        WHEN scrape_description is called
        THEN the description is found
        """
        expected_description = "Unflinching, fictional accounts of life in Ireland"

        wave_scraper.loggedin = True
        wave_scraper.load_item_page(self.ISBN)
        description = wave_scraper.scrape_description()

        assert expected_description in description

    def test_scrape_item_image_urls(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        AND a product item page
        AND we are logged in
        WHEN scrape_item_image_urls is called
        THEN a list of image URLS is found
        """
        wave_scraper.loggedin = True
        wave_scraper.load_item_page(self.ISBN)
        urls = wave_scraper.scrape_item_image_urls()
        assert len(urls) > 0

    @pytest.mark.skip("cannot run with interactive login")
    def test_not_logged_in_returns_login(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        AND we are not logged in
        WHEN load_item_page is called with an ISBN
        THEN login page is loaded
        """
        expected_url = wave_scraper.base_url + "/customers/sign_in"
        wave_scraper.loggedin = False
        wave_scraper.load_item_page(self.ISBN)
        assert wave_scraper.selenium_driver.current_url == expected_url

    def test_logged_in_returns_home(self, wave_scraper):
        """
        GIVEN a WaveScraper object
        AND we are logged in
        WHEN load_login_page is called
        THEN home page is loaded
        """
        expected_url = wave_scraper.base_url + "/"
        wave_scraper.loggedin = True
        wave_scraper.load_login_page()
        assert wave_scraper.selenium_driver.current_url == expected_url


def test_scrape_item(monkeypatch):
    """
    GIVEN a scraper object
    AND a item object
    WHEN I call scraper.scrape_item with scraper and item
    THEN the item.image_urls are updated with expected data
    AND the item.description is updated with expected data
    AND the item.dimension is updated with expected data
    """
    expected_image_urls = ["no", "way"]
    expected_description = "Dude!"
    expected_dimension = "Really, really big"
    mock_scraper = Mock()
    mock_scraper.scrape_item_image_urls.return_value = expected_image_urls
    mock_scraper.scrape_description.return_value = expected_description
    mock_scraper.scrape_dimension.return_value = expected_dimension

    description, dimension, image_urls, _ranks = scraper.scrape_item(
        mock_scraper, "12345"
    )

    assert description == expected_description
    assert dimension == expected_dimension
    assert image_urls == expected_image_urls


@patch("artemis_sg.scraper.BaseScraper.scrape_item_image_urls")
@patch("artemis_sg.scraper.BaseScraper.scrape_description")
@patch("artemis_sg.scraper.BaseScraper.scrape_dimension")
def test_scrape_item_w_rank_only_as_true(
    mock_scrape_item_image_urls,
    mock_scrape_description,
    mock_scrape_dimension,
):
    """
    GIVEN a scraper object
    AND a item object
    WHEN I call scraper.scrape_item with scraper and item
    AND with rank_only set to True
    THEN the item.image_urls are not updated
    AND the item.description is not updated
    AND the item.dimension is not updated
    """
    mock_scraper = Mock()
    rank_data = {"rank_only": True}
    description, dimension, image_urls, ranks = scraper.scrape_item(
        mock_scraper,
        "12345",
        rank_data=rank_data,
    )
    expected_call_count = 0
    assert mock_scrape_item_image_urls.call_count == expected_call_count
    assert mock_scrape_description.call_count == expected_call_count
    assert mock_scrape_dimension.call_count == expected_call_count


def test_get_item_id_tb():
    """
    GIVEN a vendor object with the "TBScraper" failover_scraper defined
    AND a item object which contains a "LINK" data element referring to a TB item
    AND a different isbn value
    WHEN I call scraper.get_item_id with vendor, and item
    THEN the TB item id is returned
    """
    isbn = "42"
    tb_id = "1234"
    link = f"https://example.com/{tb_id}/"
    vendor = Mock(name="mock_vendor")
    vendor.failover_scraper = "TBScraper"
    vendor.vendor_code = "tb"
    item = Mock()
    item.isbn = isbn
    item.data = {"LINK": link}

    i = scraper.get_item_id(vendor, item)

    assert i == tb_id


def test_get_id_tb_fail(caplog):
    """
    GIVEN a vendor object with the "TBScraper" failover_scraper defined
    AND a item object with no link
    AND a different isbn value
    WHEN I call scraper.get_item_id with vendor, and item
    THEN the isbn10 is returned
    AND an error message is logged
    """
    isbn10 = "42"
    vendor = Mock(name="mock_vendor")
    vendor.failover_scraper = "TBScraper"
    item = Mock()
    item.isbn10 = isbn10
    item.data = {"foo": "bar"}

    i = scraper.get_item_id(vendor, item)

    assert i == isbn10
    assert (
        "root",
        logging.WARNING,
        "scraper.get_item_id: No link found in item",
    ) in caplog.record_tuples


def test_get_item_id_not_tb():
    """
    Given a vendor object with the "GJScraper" failover_scraper defined
    AND a item object with an isbn attribute
    WHEN I call scraper.get_item_id with vendor and item
    THEN the isbn10 is returned
    """
    isbn10 = "42"
    vendor = Mock(name="mock_vendor")
    vendor.failover_scraper = "GJScraper"
    item = Mock()
    item.isbn10 = isbn10

    i = scraper.get_item_id(vendor, item)

    assert i == isbn10


@patch("artemis_sg.spreadsheet.get_sheet_data")
def test_update_images(mock_get_sheet_data, monkeypatch, valid_datafile):
    """
    GIVEN a vendor code, workbook and datafile
    AND the workbook has a vendor code, and "IMAGE" headers
    AND some data entries have empty img_urls
    AND those entry keys are in the isbn_key col
    AND they have a image in the "IMAGE" col
    WHEN the scraper.main is called with update_images_flag
    AND update_images is called
    THEN those entries have their img_urls updated from the sheet
    """
    with open(valid_datafile) as f:
        data = json.load(f)
    test_isbn = "9781405298056"
    test_img = "https://domain/new_img_url.jpg"
    existing_key = next(iter(data))
    data[test_isbn] = {
        "isbn10": "0123456789",
        "DESCRIPTION": "Item with no imgs",
        "image_urls": [],
    }
    prev_data = data.copy()
    with open(valid_datafile, "w") as f:
        json.dump(data, f)
    test_sheet_data = [
        ["ISBN-13", "IMAGE"],
        [test_isbn, test_img],
        [existing_key, data[existing_key]["image_urls"]],
    ]

    test_spreadsheet = Mock(name="test_spreadsheet")
    mock_get_sheet_data.side_effect = lambda *args, **kwargs: [
        row[:] for row in test_sheet_data
    ]
    vendor_code = "sample"
    worksheet = "Sheet1"
    scraper.main(
        vendor_code,
        test_spreadsheet,
        worksheet,
        valid_datafile,
        update_images_flag=True,
        update_ranks_flag=False,
    )
    with open(valid_datafile) as f:
        data = json.load(f)

    assert data[test_isbn]["image_urls"] == [test_img]
    assert data[existing_key] == prev_data[existing_key]


def test_update_images_does_not_create_new_entries(monkeypatch, valid_datafile):
    """
    GIVEN a vendor code, workbook and datafile
    WHEN the scraper.main is called with update_images_flag
    AND update_images is called
    AND an isbn does not have an entry in the datafile
    THEN a new entry is not created for that isbn
    """
    with open(valid_datafile) as f:
        data = json.load(f)
    test_isbn = "9781405298056"
    test_img = "https://domain/new_img_url.jpg"

    test_sheet_data = [["ISBN-13", "IMAGE"], [test_isbn, test_img]]
    test_sheet_data.extend([[key, test_img] for key in data])
    monkeypatch.setattr(
        scraper.spreadsheet, "get_sheet_data", lambda *_: test_sheet_data
    )
    vendor_code = "sample"
    worksheet = "Sheet1"
    scraper.main(
        vendor_code,
        worksheet,
        None,
        valid_datafile,
        update_images_flag=True,
        update_ranks_flag=False,
    )
    with open(valid_datafile) as f:
        data = json.load(f)
    assert test_isbn not in data
    assert all(
        test_img not in str(v) for inner in data.values() for v in inner.values()
    )


def test_item_needs_scraping():
    """
    GIVEN an item
    WHEN test_item_needs_scraping is called
    THEN it returns True if the item has no images
    """
    item_with_img_urls = Mock()
    item_without_img_urls = Mock()
    item_with_img_urls.isbn = "has_isbn"
    item_with_img_urls.image_urls = ["img"]
    item_without_img_urls.isbn = "has_isbn"
    item_without_img_urls.image_urls = []
    assert not scraper.item_needs_scraping(item_with_img_urls)
    assert scraper.item_needs_scraping(item_without_img_urls)


@patch("artemis_sg.scraper.choose_driver")
@patch("artemis_sg.scraper.scrape_item")
@patch("artemis_sg.scraper.rescrape_rankings")
@patch("artemis_sg.scraper.update_images")
def test_main_with_update_rank_and_update_image_flags(
    mock_update_images,
    mock_rescrape_rankings,
    mock_choose_driver,
    mock_scrape_item,
    monkeypatch,
    valid_datafile,
):
    """
    Given a vendor, Items object, and scraped datafile
    WHEN main is called with the update_rank and update_images flag
    THEN scrape_ranking and update_images is called
    """
    vendr = Mock("mock vendor")
    vendr.failover_scraper = "AmznUkScraper"
    vendr.vendor_code = "sample2"
    drivr = Mock()
    mock_choose_driver.return_value = drivr
    mock_scrape_item.return_value = (
        "",
        "",
        "",
        {"rank_only": True},
    )
    spreadsheet = Mock(name="mock_spreadsheet")
    monkeypatch.setattr(scraper, "spreadsheet", spreadsheet)
    test_sheet_data = [("ISBN", "IMAGE"), ("isbn_num", "img.jpg")]
    spreadsheet.get_sheet_data.return_value = test_sheet_data
    spreadsheet.get_sheet_keys.return_value = test_sheet_data[0]
    scraper.main(
        vendr.vendor_code,
        spreadsheet,
        None,
        valid_datafile,
        update_images_flag=True,
        update_ranks_flag=True,
    )
    mock_rescrape_rankings.assert_called()
    mock_update_images.assert_called()


@patch("artemis_sg.scraper.choose_driver")
@patch("artemis_sg.scraper.scrape_item")
def test_rescrape_rankings_calls_scrape_item(
    mock_scrape_item, mock_choose_driver, items_collection, valid_datafile
):
    """
    Given a vendor, Items object, and scraped datafile
    WHEN rescrape_rankings is run
    THEN scrape_item is called for exising titles
    """
    vendr = Mock("mock vendor")
    vendr.failover_scraper = "AmznUkScraper"
    vendr.vendor_code = "sample2"
    drivr = Mock()
    mock_choose_driver.return_value = drivr
    mock_scrape_item.return_value = (
        "",
        "",
        "",
        {"rank_only": True},
    )
    scraper.rescrape_rankings(vendr, items_collection, valid_datafile)
    num_items_in_collection_and_in_datafile = 1
    scrape_count_per_item = 2
    assert (
        mock_scrape_item.call_count
        == num_items_in_collection_and_in_datafile * scrape_count_per_item
    )
    for call_args in mock_scrape_item.call_args_list:
        args, kwargs = call_args
        assert {"rank_only": True} in args
