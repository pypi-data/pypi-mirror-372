import logging
import os.path
import re
import time  # for additional sleeps in page load.  This is a smell.
import urllib.parse
from typing import ClassVar
from urllib.parse import urlparse

from rich.console import Console
from rich.text import Text

# Selenium
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)

# Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys as SeleniumKeys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from artemis_sg import spreadsheet
from artemis_sg.config import CFG
from artemis_sg.items import Items
from artemis_sg.vendor import vendor

# Firefox
# from selenium.webdriver.firefox.service import Service as FirefoxService

MODULE = os.path.splitext(os.path.basename(__file__))[0]
console = Console()

IMG_FAILOVER_THRESHHOLD = 2


class Singleton(type):
    _instances: ClassVar[dict[type]] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseScraper:
    """
    Scraper objects know how to scrape base url
    """

    def __init__(self, selenium_driver, base_url=None, login_timeout=10):
        self.selenium_driver = selenium_driver
        if not base_url:
            self.base_url = ""
        else:
            self.base_url = base_url
        self.login_timeout = login_timeout
        self.loggedin_xpath_query = ""
        self.loggedin = False

    def load_item_page(self, item_number):
        return False

    def scrape_description(self):
        description = ""
        return description

    def scrape_dimension(self):
        dimension = ""
        return dimension

    def scrape_item_image_urls(self):
        urls = []
        return urls

    def load_login_page(self):
        pass

    def login(self):
        namespace = f"{type(self).__name__}.{self.login.__name__}"

        self.delay(2)
        input_text = Text(
            """
        ********    USER INPUT REQUIRED    ********
        Locate the selenium controlled browser
        and manually enter your login credentials.
        ********  WAITING FOR USER INPUT   ********
        """
        )
        input_text.stylize("bold cyan")
        console.print(input_text)
        try:
            WebDriverWait(self.selenium_driver, self.login_timeout).until(
                ec.presence_of_element_located((By.XPATH, self.loggedin_xpath_query))
            )
            success_text = Text(
                """
            ********      LOGIN SUCCESSFUL     ********
            ********   CONTINUING EXECUTION    ********
            """
            )
            success_text.stylize("green")
            console.print(success_text)
            self.loggedin = True
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"{namespace}: failed to login")
            logging.error(f"{namespace}: Cannot proceed.  Exiting.")
            raise e

    def delay(self, secs):
        time.sleep(secs)


class GJScraper(BaseScraper, metaclass=Singleton):
    """
    GJScraper objects know how to scrape GJ item pages
    """

    def __init__(self, selenium_driver, base_url="https://greatjonesbooks.com"):
        super().__init__(selenium_driver, base_url)
        self.timeout = 3
        self.loggedin_xpath_query = "//a[@href='/account']"

    def load_item_page(self, item_number, tries=0):
        namespace = f"{type(self).__name__}.{self.load_item_page.__name__}"

        # GJ does not maintain session if the links on page are not used
        # if not logged in, then build url; else use search facility
        try:
            self.delay(1)
            WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located(
                    (By.XPATH, "//a[@href='/account' and text()='Account Summary']")
                )
            )
        except (NoSuchElementException, TimeoutException):
            start = "/product/"
            url = self.base_url + start + item_number
            self.selenium_driver.get(url)
            return True
        try:
            search = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.XPATH, "//a[@href='/search']"))
            )
            search.click()
            self.delay(2)

            # wait until Publisher list is populated
            # by finding sentinel publisher
            sentinel = CFG["asg"]["scraper"]["gjscraper"]["sentinel_publisher"]
            timeout_bak = self.timeout
            self.timeout = 60
            WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located(
                    (By.XPATH, f"//option[@value='{sentinel}']")
                )
            )
            self.timeout = timeout_bak
            # then get itemCode field for search
            item_field = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.XPATH, "//input[@name='itemCode']"))
            )
            search_button = self.selenium_driver.find_element(
                By.CSS_SELECTOR, ".buttonSet > button:nth-child(1)"
            )
            clear_button = self.selenium_driver.find_element(
                By.CSS_SELECTOR, ".buttonSet > button:nth-child(2)"
            )
            clear_button.click()
            item_field.send_keys(item_number)
            self.delay(2)
            search_button.click()
            self.delay(2)
            # check for No Results
            e = self.selenium_driver.find_element(
                By.XPATH, "//div[@class='formBox']/div"
            )
            if "No Results" in e.text:
                # Do not continue to try
                logging.info(f"{namespace}: No Results found for {item_number}")
                return False
            items = self.selenium_driver.find_elements(By.ID, "product.item_id")
            items[0].click()
            return True
        except (NoSuchElementException, TimeoutException, IndexError):
            tries += 1
            if tries < self.timeout:
                self.load_item_page(item_number, tries)
            else:
                logging.info(f"{namespace}: failed item search for {item_number}")
                return False

    def scrape_description(self):
        try:
            self.delay(1)
            elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "desc"))
            )
            span = elem.find_element(By.CLASS_NAME, "short-comments")
            description = span.text
        except (NoSuchElementException, TimeoutException):
            description = ""

        return description

    def scrape_item_image_urls(self):
        namespace = f"{type(self).__name__}.{self.scrape_item_image_urls.__name__}"

        urls = []
        try:
            self.delay(1)
            # GJ appears to only have single cover images
            elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "cover"))
            )
            img = elem.find_element(By.TAG_NAME, "img")
            src = img.get_attribute("src")
            if src and "noimage.png" not in src:
                urls.append(src)
        except (NoSuchElementException, TimeoutException) as e:
            logging.warning(f"{namespace}: error {e}")
        return urls

    def load_login_page(self):
        # Load search page while logged out in an attempt to get the
        # Publishers list to populate when the page is loaded after login.
        self.selenium_driver.get(self.base_url + "/search")
        self.delay(self.timeout)
        login = "/login"
        url = self.base_url + login
        self.selenium_driver.get(url)

    def add_to_cart(self, qty):
        # TODO: Can we DRY this up?  Some duplication between scrapers
        namespace = f"{type(self).__name__}.{self.add_to_cart.__name__}"

        self.delay(1)
        stock_elem = self.selenium_driver.find_element(By.CLASS_NAME, "on-hand")
        m = re.search(r"([0-9]+) in stock", stock_elem.text)
        if m:
            stock = m.group(1)
            if int(stock) < int(qty):
                qty = stock
        self.delay(1)
        try:
            # gather html elements needed
            add_div = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "add"))
            )
            qty_field = add_div.find_element(By.XPATH, "//input[@name='qty']")

            qty_field.clear()
            qty_field.send_keys(qty + SeleniumKeys.ENTER)
        except (NoSuchElementException, TimeoutException) as e:
            logging.warning(f"{namespace}: error {e}")
            return 0
        return int(qty)

    def load_cart_page(self):
        # TODO: Can we DRY this up?  Some duplication between scrapers
        namespace = f"{type(self).__name__}.{self.load_cart_page.__name__}"
        try:
            cart = self.selenium_driver.find_element(By.CLASS_NAME, "cart")
            cart.click()
            self.delay(1)
            cart.click()
            self.delay(1)
        except Exception as e:
            logging.warning(f"{namespace}: error {e}")
            return False
        return True

    def scrape_error_msg(self):
        try:
            elem = self.selenium_driver.find_element(By.CLASS_NAME, "errorMsg")
            msg = elem.text
        except NoSuchElementException:
            msg = ""
        return msg


class SDScraper(BaseScraper, metaclass=Singleton):
    """
    SDScraper objects know how to scrape SD item pages
    """

    def __init__(self, selenium_driver, base_url="https://strathearndistribution.com"):
        super().__init__(selenium_driver, base_url)
        self.timeout = 3
        self.loggedin_xpath_query = "//span[text()='My lists']"

    def load_login_page(self):
        namespace = f"{type(self).__name__}.{self.load_login_page.__name__}"
        try:
            self.selenium_driver.get(self.base_url)
            self.delay(2)
            login_xpath = "//span[contains(text(), 'Login')]"
            button = self.selenium_driver.find_element(By.XPATH, login_xpath)
            button.click()
        except (
            StaleElementReferenceException,
            NoSuchElementException,
            TimeoutException,
        ) as e:
            logging.error(f"{namespace}: failed to load login page")
            logging.error(f"{namespace}: Cannot proceed.  Exiting.")
            raise e

    def load_item_page(self, item_number, tries=0):
        namespace = f"{type(self).__name__}.{self.load_item_page.__name__}"
        try:
            self.selenium_driver.get(self.base_url)
            self.delay(2)
            search = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.ID, "search"))
            )
            search.send_keys(item_number + SeleniumKeys.ENTER)
            self.delay(2)
            elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "listItem"))
            )
            self.delay(2)
            elem.click()
            return True
        except (
            StaleElementReferenceException,
            NoSuchElementException,
            TimeoutException,
        ) as e:
            tries += 1
            if tries < self.timeout:
                self.load_item_page(item_number, tries)
            else:
                logging.warning(
                    f"{namespace}: Failed to load item page '{item_number}': {e}"
                )
                return False

    def scrape_description(self):
        try:
            # rc-* IDs are dynamic, must use classes
            elem = self.selenium_driver.find_element(By.CLASS_NAME, "ant-tabs-nav-list")
            tab_btn = elem.find_element(By.CLASS_NAME, "ant-tabs-tab-btn")
            tab_btn.click()
            pane = self.selenium_driver.find_element(By.CLASS_NAME, "ant-tabs-tabpane")
            description = pane.text
        except NoSuchElementException:
            description = ""

        return description

    def scrape_dimension(self):
        try:
            dets_xpath = "//div[@class='ant-tabs-tab-btn'][text()='Details']"
            btn = self.selenium_driver.find_element(By.XPATH, dets_xpath)
            btn.click()
            elem = self.selenium_driver.find_element(
                By.XPATH, "//div[strong[contains(text(), 'Physical Dimensions:')]]"
            )
            t = elem.text
            dimension = t.replace("Physical Dimensions:\n", "")
        except NoSuchElementException:
            dimension = ""

        return dimension

    def scrape_item_image_urls(self):
        namespace = f"{type(self).__name__}.{self.scrape_item_image_urls.__name__}"
        urls = []
        try:
            # main only
            elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "full-image"))
            )
            src = elem.get_attribute("src")
            if src:
                urls.append(src)
            # ensure we are seeing the top of the page
            html = self.selenium_driver.find_element(By.TAG_NAME, "html")
            html.send_keys(SeleniumKeys.PAGE_UP)
            # image gallery for additional images
            elems = self.selenium_driver.find_elements(By.CLASS_NAME, "gallery-vert")
            for elem in elems:
                src = elem.get_attribute("src")
                if src:
                    urls.append(src)
        except NoSuchElementException as e:
            logging.warning(f"{namespace}: error {e}")
        return urls

    def add_to_cart(self, qty):
        namespace = f"{type(self).__name__}.{self.add_to_cart.__name__}"

        self.delay(1)
        # try:???
        stock_elem = self.selenium_driver.find_element(
            By.XPATH, "//span[contains(text(), 'in stock')]"
        )
        m = re.search(r"([0-9]+) in stock", stock_elem.get_attribute("innerHTML"))
        if m:
            stock = m.group(1)
            if int(stock) < int(qty):
                qty = stock
        self.delay(1)
        try:
            # gather html elements needed
            elems = self.selenium_driver.find_elements(By.CLASS_NAME, "ant-btn-primary")
            button = None
            for e in elems:
                if "Add to cart" in e.text:
                    button = e
                    break
            qty_field = self.selenium_driver.find_element(
                By.XPATH,
                (
                    "//input[@class='ant-input' and @type='text' "
                    "and not(ancestor::div[contains(@class, '-block')])]"
                ),
            )
            # the qty field must be clicked to highlight amount.  Clearing doesn't work
            qty_field.click()
            qty_field.send_keys(qty)
            button.click()
        except Exception as e:
            logging.warning(f"{namespace}: error {e}")
            return 0
        return int(qty)

    def load_cart_page(self):
        namespace = f"{type(self).__name__}.{self.load_cart_page.__name__}"
        try:
            cart = "/checkout/cart"
            url = self.base_url + cart
            self.selenium_driver.get(url)
            self.delay(1)
            return True
        except Exception as e:
            logging.warning(f"{namespace}: error {e}")
            return False


class TBScraper(BaseScraper, metaclass=Singleton):
    """
    TBScraper objects know how to scrape TB item pages
    """

    def __init__(self, selenium_driver, base_url="https://texasbookman.com/"):
        super().__init__(selenium_driver, base_url)
        self.timeout = 3
        self.loggedin_xpath_query = "//a[@href='/admin']"

    def load_item_page(self, item_number):
        start = "p/"
        url = self.base_url + start + item_number
        self.selenium_driver.get(url)
        return True

    def scrape_description(self):
        try:
            elem = self.selenium_driver.find_element(
                By.CLASS_NAME, "variant-description"
            )
            text = elem.text
            description = text.replace("NO AMAZON SALES\n\n", "")
        except NoSuchElementException:
            description = ""

        return description

    def scrape_dimension(self):
        try:
            elem = self.selenium_driver.find_element(By.CLASS_NAME, "full-description")
            m = re.search(r"(Size:.+)\n", elem.text)
            dimension = m.group(1).replace("Size:", "").strip()
        except (NoSuchElementException, AttributeError):
            dimension = ""

        return dimension

    def scrape_item_image_urls(self):
        urls = []
        try:
            elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "a-left"))
            )
            elem = self.selenium_driver.find_element(By.CLASS_NAME, "picture-thumbs")
            left = elem.find_element(By.CLASS_NAME, "a-left")
            left.click()
            while True:
                self.delay(2)
                thumb = self._get_thumb_from_slimbox()
                if thumb:
                    urls.append(thumb)
                next_link = WebDriverWait(self.selenium_driver, self.timeout).until(
                    ec.presence_of_element_located((By.ID, "lbNextLink"))
                )
                self.delay(2)
                next_link.click()
        except (
            NoSuchElementException,
            ElementNotInteractableException,
            TimeoutException,
        ):
            try:
                elem = self.selenium_driver.find_element(By.CLASS_NAME, "picture")
                img = elem.find_element(By.TAG_NAME, "img")
                thumb = img.get_attribute("src")
                urls.append(thumb)
            except NoSuchElementException:
                pass

        return urls

    def _get_thumb_from_slimbox(self):
        timeout = 3
        thumb = None
        try:
            img_div = WebDriverWait(self.selenium_driver, timeout).until(
                ec.presence_of_element_located((By.ID, "lbImage"))
            )
            style = img_div.get_attribute("style")
            m = re.search('"(.*)"', style)
            if m:
                thumb = m.group(1)
        except (NoSuchElementException, TimeoutException):
            pass

        return thumb

    def load_login_page(self):
        login = "login"
        url = self.base_url + login
        self.selenium_driver.get(url)

    def impersonate(self, email):
        namespace = f"{type(self).__name__}.{self.impersonate.__name__}"

        # Go to /Admin/Customer/List
        customers = "/Admin/Customer/List"
        url = self.base_url + customers
        self.selenium_driver.get(url)
        self.delay(1)
        try:
            # search for email
            search_email = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.ID, "SearchEmail"))
            )
            search_email.clear()
            search_email.send_keys(email + SeleniumKeys.ENTER)
            # Get customer link associated with email
            email_xpath = (
                f"//div[@id='customers-grid']/table/tbody/tr/td/a[text()='{email}']"
            )
            customer_link = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.XPATH, email_xpath))
            )
            links = self.selenium_driver.find_elements(By.XPATH, email_xpath)
            # Bail if multiple customer records for given email.
            if len(links) > 1:
                logging.error(
                    f"{namespace}: Found multiple customer records for email "
                    f"'{email}' to impersonate"
                )
                logging.error(f"{namespace}: Cannot proceed.  Exiting.")
                raise Exception
            customer_link.click()
            # click "Place Order (impersonate)"
            impersonate = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located(
                    (By.XPATH, "//a[text()='Place order (Impersonate)']")
                )
            )
            impersonate.click()
            # click "Place Order" button
            button = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located(
                    (By.XPATH, "//input[@name='impersonate']")
                )
            )
            button.click()
            self.delay(1)
            WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "finish-impersonation"))
            )
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"{namespace}: failed to impersonate")
            logging.error(f"{namespace}: Cannot proceed.  Exiting.")
            raise e
        return True

    def add_to_cart(self, qty):
        namespace = f"{type(self).__name__}.{self.add_to_cart.__name__}"

        qty = int(qty)
        self.delay(1)
        stock_elem = self.selenium_driver.find_element(By.CLASS_NAME, "stock")
        m = re.search(r"Availability: ([0-9]+) in stock", stock_elem.text)
        if m:
            stock = m.group(1)
            stock = int(stock)
            qty = min(qty, stock)
        try:
            # gather html elements needed
            qty_field = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "qty-input"))
            )
            button = self.selenium_driver.find_element(
                By.CLASS_NAME, "add-to-cart-button"
            )
            qty_field.clear()
            # ENTERing out of the qty_field DOES NOT add to cart.
            # The button must be clicked instead.
            qty_field.send_keys(qty)
            button.click()
            self.delay(1)
        except Exception as e:
            logging.warning(f"{namespace}: error {e}")
            return 0
        return qty

    def load_cart_page(self):
        cart = "cart"
        url = self.base_url + cart
        self.selenium_driver.get(url)
        return True

    def search_item_num(self, search):
        namespace = f"{type(self).__name__}.{self.search_item_num.__name__}"

        item_num = ""
        search = urllib.parse.quote_plus(search)
        url = self.base_url + "search?q=" + search
        self.selenium_driver.get(url)
        self.delay(2)
        timeout_bak = self.timeout
        self.timeout = 120
        WebDriverWait(self.selenium_driver, self.timeout).until(
            ec.presence_of_element_located((By.CLASS_NAME, "search-results"))
        )
        self.timeout = timeout_bak
        links = self.selenium_driver.find_elements(
            By.XPATH, "//div[@class='search-results']//a[contains(@href, '/p/')]"
        )
        if links:
            item_urls = [x.get_attribute("href") for x in links]
            for item_url in item_urls:
                m = re.search(r"\/p\/([0-9]+)\/(?!uk-)", item_url)
                if m:
                    item_num = m.group(1)
                    break
        else:
            logging.warning(f"{namespace}: Failed to find item using q='{search}'")
        return item_num


class AmznScraper(BaseScraper, metaclass=Singleton):
    """
    AmznScraper objects know how to scrape amazon item pages
    """

    def __init__(self, selenium_driver, base_url="https://www.amazon.com/"):
        super().__init__(selenium_driver, base_url)
        self.timeout = 1

    def load_item_page(self, item_number):
        start = "dp/"
        url = self.base_url + start + item_number
        self.selenium_driver.get(url)
        return True

    def scrape_description(self):
        description = ""
        description = self._scrape_amazon_editorial_review()
        if not description:
            description = self._scrape_amazon_description()

        return description

    def scrape_dimension(self):
        dimension = ""
        try:
            xpath = "//span/span[contains(text(), 'Dimensions')]//following::span"
            elem = self.selenium_driver.find_element(By.XPATH, xpath)
            dimension = elem.get_attribute("innerHTML")
        except NoSuchElementException:
            dimension = ""
        return dimension

    def _scrape_amazon_editorial_review(self):
        descr = ""
        try:
            elem = self.selenium_driver.find_element(
                By.ID, "editorialReviews_feature_div"
            )
            text = elem.text
            descr_lines = re.split("^.*\\n.*\\n", text)  # trim off first two lines
            descr = descr_lines[-1]
        except NoSuchElementException:
            descr = ""

        return descr

    def _scrape_amazon_description(self):
        descr = ""
        try:
            elem = self.selenium_driver.find_element(
                By.ID, "bookDescription_feature_div"
            )
            # read_more = elem.find_element(By.CLASS_NAME, 'a-expander-prompt')
            # read_more.click()
            descr = elem.text
        except NoSuchElementException:
            descr = ""

        return descr

    def get_span_type_thumb_id_prefix(self):
        """Get span_type and thumb_id_prefix from amazon images widget."""
        namespace = (
            f"{type(self).__name__}.{self.get_span_type_thumb_id_prefix.__name__}"
        )
        span_type = None
        thumb_id_prefix = None
        try:
            span = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.ID, "imgThumbs"))
            )
            span_type = "imgThumbs"
        except (NoSuchElementException, TimeoutException):
            logging.info(f"{namespace}: No imgThumbs id, trying imgTagWrapperID")
            try:
                span = WebDriverWait(self.selenium_driver, self.timeout).until(
                    ec.presence_of_element_located((By.ID, "imgTagWrapperId"))
                )
                span_type = "imgTagWrapperId"
            except (NoSuchElementException, TimeoutException):
                logging.info(f"{namespace}: No imgTagWrapperId id")
                logging.info(f"{namespace}: Returning empty urls list")
                return (span_type, thumb_id_prefix)

        if span_type == "imgThumbs":
            link = span.find_element(By.CLASS_NAME, "a-link-normal")
            thumb_id_prefix = "ig-thumb-"
        else:
            link = span
            thumb_id_prefix = "ivImage_"
        try:
            link.click()
        except ElementClickInterceptedException:
            logging.info(f"{namespace}: Failed to click images widget")
            logging.info(f"{namespace}: Returning empty urls list")
            return (span_type, thumb_id_prefix)
        return (span_type, thumb_id_prefix)

    def _get_image_urls_from_widget(self, span_type, thumb_id_prefix):
        namespace = f"{type(self).__name__}.{self._get_image_urls_from_widget.__name__}"
        counter = 0
        urls = []
        while True:
            try:
                thumb = ""
                xpath = f"//*[@id='{thumb_id_prefix}{counter}']"
                elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                    ec.presence_of_element_located((By.XPATH, xpath))
                )
                if span_type == "imgThumbs":
                    thumb = elem.get_attribute("src")
                if span_type == "imgTagWrapperId":
                    inner_elem = elem.find_element(By.CLASS_NAME, "ivThumbImage")
                    style = inner_elem.get_attribute("style")
                    m = re.search('"(.*)"', style)
                    if m:
                        thumb = m.group(1)
                sub, suff = os.path.splitext(thumb)
                indx = sub.find("._")
                url = sub[:indx] + suff
                if url:
                    urls.append(url)
                logging.debug(f"{namespace}: Thumbnail src is {thumb}")
                logging.debug(f"{namespace}: Full size URL is {url}!r")
                counter += 1
            except (NoSuchElementException, TimeoutException):
                break
        return urls

    def scrape_item_image_urls(self):
        namespace = f"{type(self).__name__}.{self.scrape_item_image_urls.__name__}"
        urls = []
        span_type, thumb_id_prefix = self.get_span_type_thumb_id_prefix()
        if thumb_id_prefix:
            logging.debug(f"{namespace}: Clicked images widget")
            urls += self._get_image_urls_from_widget(span_type, thumb_id_prefix)
        else:
            try:
                # amazon.co.uk sometimes does not have an image widget
                elem = WebDriverWait(self.selenium_driver, self.timeout).until(
                    ec.presence_of_element_located((By.ID, "main-image"))
                )
                url = elem.get_attribute("src")
                if url:
                    urls.append(url)
            except (NoSuchElementException, TimeoutException):
                pass

        # amazon adds stupid human holding book images
        # remove this
        if len(urls) > 1:
            urls.pop()

        return urls

    def scrape_rank(self):
        """
        GIVEN the AmznScraper, a driver, and Item
        WHEN the item page is loaded
        AND the AmznScraper.scrape_rank method is called
        THEN the rank number from Bestsellers "# in Books' is returned
        """
        try:
            rank_li = self.selenium_driver.find_element(
                By.XPATH, "//li[span/span[contains(text(),'Best Sellers Rank')]]"
            )
            rank_text = rank_li.text
            match = re.search(r"([\d,]+) in Books", rank_text)
            rank = match.group(1) if match else ""
        except NoSuchElementException:
            rank = ""
        return rank


class AmznUkScraper(AmznScraper, metaclass=Singleton):
    """
    AmznUkScraper objects know how to scrape amazon.co.uk item pages
    """

    def __init__(self, selenium_driver, base_url="https://www.amazon.co.uk/"):
        super().__init__(selenium_driver, base_url)
        self.decline_cookies()

    def decline_cookies(self):
        try:
            decline_button = self.selenium_driver.find_element(
                By.ID, "sp-cc-rejectall-link"
            )
            decline_button.click()
            self.delay(2)
            return True
        except (NoSuchElementException, TimeoutException):
            return False


class WaveScraper(BaseScraper, metaclass=Singleton):
    """
    WaveScraper objects know how to scrape Wave item pages
    """

    def __init__(
        self,
        selenium_driver,
        base_url="https://artemisbooksales.b2bwave.com",
        timeout=3,
        login_timeout=CFG["asg"]["scraper"]["login_timeout"],
    ):
        super().__init__(selenium_driver, base_url, login_timeout)
        self.timeout = timeout
        self.loggedin_xpath_query = "//*[contains(@class, 'btn-log-out')]"

    def load_home_page(self):
        self.selenium_driver.get(self.base_url)

    def load_login_page(self):
        if self.loggedin:
            self.load_home_page()
        else:
            self.selenium_driver.get(self.base_url + "/customers/sign_in")
            WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "login-form"))
            )

    def login(self):
        try:
            self.selenium_driver.find_element(By.CLASS_NAME, "btn-log-out")
        except NoSuchElementException:
            self.load_login_page()
            super().login()

    def item_search(self, item_num):
        try:
            self.selenium_driver.get(self.base_url)
            # search for item number
            search_field = WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "product-search"))
            )
            search_field.send_keys(item_num + SeleniumKeys.ENTER)
            # select first item in list
            WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located(
                    (By.XPATH, "//*[@class='product-title']//a")
                )
            )
            item = self.selenium_driver.find_elements(
                By.XPATH, "//*[contains(@class, 'line-item code')]//a"
            )[0]
            item_url = item.get_attribute("href")
            item_code = item.text
        except (NoSuchElementException, IndexError):
            item_url = None
        if item_code == item_num:
            return item_url

    def load_item_page(self, item_num):
        if not self.loggedin:
            self.login()
        url = self.item_search(item_num)
        try:
            self.selenium_driver.get(url)
            WebDriverWait(self.selenium_driver, self.timeout).until(
                ec.presence_of_element_located((By.CLASS_NAME, "copyrite"))
            )
        except WebDriverException:
            return False
        return True

    def scrape_description(self):
        try:
            elem = self.selenium_driver.find_element(
                By.XPATH, "//*[@id='single-product-description']//div//p"
            )
        except NoSuchElementException:
            return ""
        return elem.text

    def scrape_item_image_urls(self):
        try:
            elems = self.selenium_driver.find_elements(
                By.XPATH, "//*[@id='carouselProduct']//a//img"
            )
        except NoSuchElementException:
            return []
        urls = [x for x in (elem.get_attribute("src") for elem in elems) if x]
        return urls


##############################################################################
# utility functions
##############################################################################
def get_headless_driver():
    return get_driver("--headless=new")


def get_driver(option_args: str = ""):
    """Creates a new instance of the chrome driver.

    :param option_args:
       Option arguments to pass to the driver
    :returns: selenium.webdriver object
    """
    namespace = f"{MODULE}.{get_driver.__name__}"
    service = ChromeService()
    options = webdriver.ChromeOptions()
    # Convert userAgent to Linux if Windows.
    # Have to get userAgent first.
    if option_args:
        options.add_argument(option_args)
        logging.info(f"{namespace}: Setting webdriver option to '{option_args}'.")
    driver = webdriver.Chrome(service=service, options=options)

    agent_str = driver.execute_script("return navigator.userAgent")

    pat = re.compile(r"\(Windows.+?\)")
    new_agent = pat.sub(r"(X11; Linux x86_64)", agent_str)
    if new_agent != agent_str:
        driver.close()
        logging.info(f"{namespace}: Setting webdriver user-agent to '{new_agent}'.")
        options.add_argument(f"user-agent={new_agent}")
        driver = webdriver.Chrome(service=service, options=options)

    return driver


def scrape_item(
    scrapr,
    item_id,
    description="",
    dimension="",
    image_urls=None,
    rank_data=None,
):
    """
    Scraped an item using the scrapr and the item_id
    :param scrapr: Scraper object
    :param item_id: string id of item
    :param description: string
    :param dimension: string
    :param image_urls: list of strings
    :param rank_data: dict with keys "AMAZON", "AMAZON_UK", "rank_only
    :returns: description, dimension, image_urls, ranks
    """
    if image_urls is None:
        image_urls = []
    if rank_data is None:
        rank_data = {"rank_only": False}
    namespace = f"{MODULE}.{scrape_item.__name__}"
    scrapr.load_item_page(item_id)
    logging.info(
        f"{namespace}: Getting item image urls via {scrapr.__class__.__name__}"
    )
    if isinstance(scrapr, AmznScraper):
        if isinstance(scrapr, AmznUkScraper):
            rank_data["AMAZON_UK"] = scrapr.scrape_rank()
        else:
            rank_data["AMAZON"] = scrapr.scrape_rank()
    if rank_data.get("rank_only"):
        return description, dimension, image_urls, rank_data
    l_image_urls = scrapr.scrape_item_image_urls()
    if image_urls and len(l_image_urls) > 1:
        l_image_urls.pop(0)
    image_urls = image_urls + l_image_urls
    logging.info("     URLs: {image_urls!r}")
    if image_urls and not description:
        logging.info(
            f"{namespace}: Getting description via {scrapr.__class__.__name__}"
        )
        description = scrapr.scrape_description()
        logging.info("     Description: {description[:140]!r}")
    if image_urls and not dimension:
        logging.info(f"{namespace}: Getting dimension via {scrapr.__class__.__name__}")
        dimension = scrapr.scrape_dimension()
        logging.info("     Dimension: {dimension[:140]!r}")

    return description, dimension, image_urls, rank_data


def get_item_id(vendr, item):
    namespace = f"{MODULE}.{get_item_id.__name__}"
    item_id = item.isbn10 or item.isbn
    if vendr.failover_scraper == "TBScraper":
        try:
            url = item.data["LINK"]
            m = re.search(r"\/([0-9]+)\/", url)
            if m:
                item_id = m.group(1)
        except KeyError:
            logging.warning(f"{namespace}: No link found in item")
    if vendr.failover_scraper in ("SDScraper", "WaveScraper"):
        item_id = item.isbn
    return item_id


def update_images(vendr_code, scraped_items_db, sheet_data, sheet_keys):
    """
    Updates images for existing data using the image column defined in config.
    """
    namespace = f"{MODULE}.{update_images.__name__}"
    vendr = vendor(vendr_code)
    isbn_key = vendr.isbn_key
    items_obj = Items(sheet_keys, sheet_data, isbn_key)
    existing_data = items_obj.get_json_data_from_file(scraped_items_db)
    existing_keys = [item.isbn for item in items_obj if item.isbn in existing_data]
    items_obj.load_scraped_data(scraped_items_db)
    img_key_name = CFG["asg"]["spreadsheet"]["update_images_from"].strip().upper()
    supported_img_exts = CFG["asg"]["data"]["supported_img_formats"]
    try:
        sheet_keys.index(img_key_name)
    except ValueError as e:
        err = f"Cannot find column '{img_key_name}'"
        raise IndexError(err) from e
    for item in items_obj:
        if item.isbn not in existing_keys:
            logging.info(f"{namespace}: ISBN '{item.isbn}' not in database, skipping")
            continue
        if item.image_urls:
            logging.info(
                f"{namespace}: ISBN '{item.isbn}' already has images, skipping"
            )
            continue

        new_img = item.data.get(img_key_name)

        if new_img:
            parsed = urlparse(new_img)
            _, ext = os.path.splitext(parsed.path)
            if (
                parsed.scheme in ("http", "https")
                and parsed.netloc
                and ext in supported_img_exts
            ):
                item.image_urls.append(new_img)
                logging.info(
                    f"{namespace}: Updating '{item.isbn}' with image '{new_img}'"
                )
                items_obj.save_scraped_data(scraped_items_db)
            else:
                logging.info(f"{namespace}: Img URL'{new_img}'is invalid, skipping")


def rescrape_rankings(vendr, items_obj, scraped_items_db):
    namespace = f"{MODULE}.{rescrape_rankings.__name__}"
    existing_data = items_obj.get_json_data_from_file(scraped_items_db)
    existing_keys = [item.isbn for item in items_obj if item.isbn in existing_data]
    items_obj.load_scraped_data(scraped_items_db)
    driver = None
    for item in items_obj:
        rank_data = {"rank_only": True}
        if not item.isbn:
            logging.info("No isbn for item, skipping lookup")
            continue
        if item.isbn not in existing_keys:
            logging.info(f"{namespace}: ISBN '{item.isbn}' not in database, skipping")
            continue
        driver = driver if driver else choose_driver()
        prime_scrapr = AmznScraper(driver)
        _desc, _dim, _imgs, rank_data = scrape_item(
            prime_scrapr, item.isbn10, None, None, None, rank_data
        )
        failover_scrapr = (
            globals()[vendr.failover_scraper](driver)
            if vendr.failover_scraper
            else None
        )
        if failover_scrapr:
            item_id = get_item_id(vendr, item)
            _desc, _dim, _imgs, rank_data = scrape_item(
                failover_scrapr,
                item_id,
                _desc,
                _dim,
                _imgs,
                rank_data,
            )
        set_rank_data(rank_data, item)
        items_obj.save_scraped_data(scraped_items_db)

    if driver:
        driver.quit()


def set_rank_data(rank_data, item):
    for key in ("AMAZON", "AMAZON_UK"):
        if key in rank_data and rank_data.get(key):
            item.data["RANKS"][key] = rank_data.get(key)


def item_needs_scraping(item):
    """
    If an item has no isbn or already has images, return False
    """
    if not item.isbn:
        logging.info("No isbn for item, skipping lookup")
        return False

    if item.image_urls != []:
        logging.info(f"{item.isbn} found in database, skipping")
        return False
    return True


def choose_driver():
    logging.info("Opening browser...")
    if CFG["asg"]["scraper"]["headless"]:
        driver = get_headless_driver()
    else:
        driver = get_driver()
    return driver


def main(
    vendor_code,
    sheet_id,
    worksheet,
    scraped_items_db,
    update_images_flag,
    update_ranks_flag,
):
    namespace = f"{MODULE}.{main.__name__}"
    # get vendor info from database
    logging.debug(f"{namespace}: Instantiate vendor.")
    vendr = vendor(vendor_code)

    sheet_data = spreadsheet.get_sheet_data(sheet_id, worksheet)

    sheet_keys = [x for x in sheet_data.pop(0) if x]  # filter out None
    items_obj = Items(sheet_keys, sheet_data, vendr.isbn_key)

    if update_images_flag:
        update_images(vendor_code, scraped_items_db, sheet_data, sheet_keys)
    if update_ranks_flag:
        rescrape_rankings(vendr, items_obj, scraped_items_db)
    if update_images_flag or update_ranks_flag:
        return

    items_obj.load_scraped_data(scraped_items_db)
    driver = None
    for item in items_obj:
        if not item_needs_scraping(item):
            continue
        description = ""
        dimension = ""
        image_urls = []
        logging.info(f"{namespace}: Searching for {item.isbn} ...")

        driver = driver if driver else choose_driver()
        prime_scrapr = AmznScraper(driver)

        logging.info(f"{namespace}: No scraped data currently: {item.isbn}")
        description, dimension, image_urls, rank_data = scrape_item(
            prime_scrapr,
            item.isbn10,
            description,
            dimension,
            image_urls,
        )
        failover_scrapr = (
            globals()[vendr.failover_scraper](driver)
            if vendr.failover_scraper
            else None
        )
        if failover_scrapr and len(image_urls) < IMG_FAILOVER_THRESHHOLD:
            item_id = get_item_id(vendr, item)
            description, dimension, image_urls, ranks = scrape_item(
                failover_scrapr,
                item_id,
                description,
                dimension,
                image_urls,
                rank_data,
            )
        elif (
            failover_scrapr
            and isinstance(failover_scrapr, AmznUkScraper)
            and not item.data.get("RANKS", {}).get("AMAZON_UK")
        ):  # only need rank
            item_id = get_item_id(vendr, item)
            rank_data["rank_only"] = True
            description, dimension, image_urls, ranks = scrape_item(
                failover_scrapr,
                item_id,
                description,
                dimension,
                image_urls,
                rank_data,
            )
        item.data["DESCRIPTION"] = description
        item.data["DIMENSION"] = dimension
        item.image_urls = image_urls
        set_rank_data(rank_data, item)
        # Save db after every item scraping
        logging.info(f"{namespace}: Saving scraped item {item.isbn} to database")
        items_obj.save_scraped_data(scraped_items_db)

    if driver:
        logging.info(f"{namespace}: Closing browser...")
        driver.quit()
