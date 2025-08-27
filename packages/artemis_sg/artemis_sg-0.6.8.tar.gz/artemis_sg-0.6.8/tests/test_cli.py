# ruff: noqa: S101
import os.path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from artemis_sg import cli


def test_scrape_without_vendor(monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called without a vendor argument
    THEN helpful text is displayed
    """
    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["scrape"])

    assert "skipping due to lack of VENDOR" in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_scrape_with_args(option, monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called with a vendor argument
    AND a sheet_id argument
    AND a worksheet argument
    THEN scraper is run with vendor
    AND debug mode is enabled
    """
    expected_path = os.path.join("foo", "bar")
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    worksheet = "TEST_SHEET_TAB"
    expected_msg = (
        f"Scraping web data for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"saving data to '{expected_path}'..."
    )

    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["-v", vendor_code, "-b", workbook, option, worksheet, "scrape"]
    )

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_scrape_without_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called with a vendor argument
    AND a sheet_id argument
    AND the debug flag
    THEN scraper is run with vendor
    AND debug mode is enabled
    """
    expected_path = os.path.join("foo", "bar")
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    expected_msg = (
        f"Scraping web data for '{vendor_code}' "
        f"using '{workbook}':'', "
        f"saving data to '{expected_path}'..."
    )

    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["-v", vendor_code, "-b", workbook, "scrape"])

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_scrape_with_rescrape_option(monkeypatch):
    expected_path = os.path.join("foo", "bar")
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    worksheet = "TEST_SHEET_TAB"
    expected_msg = (
        f"Re-scraping rank data for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"saving data to '{expected_path}'..."
    )

    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            "-s",
            worksheet,
            "scrape",
            "--update-ranks",
        ],
    )

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_download(monkeypatch):
    """
    GIVEN cli
    WHEN the download sub-command is called
    THEN image downloader is run
    """
    monkeypatch.setattr(cli, "img_downloader_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["download"])

    assert result.exit_code == 0
    assert "Downloading images..." in result.output


def test_upload(monkeypatch):
    """
    GIVEN cli
    WHEN the upload sub-command is called
    THEN Google Cloud uploader is run
    """
    monkeypatch.setattr(cli, "gcloud_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["upload"])

    assert result.exit_code == 0
    assert "Uploading images to Google Cloud..." in result.output


@pytest.mark.parametrize("s_option", ("-s", "--worksheet"))
@pytest.mark.parametrize("t_option", ("-t", "--title"))
def test_generate(s_option, t_option, monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called with a title and vendor
    THEN slide generator is run with given title and vendor
    """
    title = "Badass Deck"
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    worksheet = "TEST_WORKSHEET"
    expected_msg = (
        f"Creating Google Slides deck '{title}' for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}'..."
    )

    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            s_option,
            worksheet,
            "generate",
            t_option,
            title,
        ],
    )

    assert result.exit_code == 0
    assert expected_msg in result.output


@pytest.mark.parametrize("s_option", ("-s", "--worksheet"))
def test_generate_no_title(s_option, monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a title
    AND with a vendor
    THEN slide generator is run with default title
    """
    title = "New Arrivals"
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    worksheet = "TEST_WORKSHEET"
    expected_msg = (
        f"Creating Google Slides deck '{title}' for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}'..."
    )

    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["-v", vendor_code, "-b", workbook, s_option, worksheet, "generate"]
    )

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_generate_no_title_no_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a title
    AND without a worksheet
    AND with a vendor
    THEN slide generator is run with default title
    AND default worksheet
    """
    title = "New Arrivals"
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    expected_msg = (
        f"Creating Google Slides deck '{title}' for '{vendor_code}' "
        f"using '{workbook}':''..."
    )

    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["-v", vendor_code, "-b", workbook, "generate"])

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_generate_no_vendor(monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a vendor
    THEN helpful text is displayed
    """
    monkeypatch.setattr(
        cli,
        "slide_generator_wrapper",
        lambda *args: (_ for _ in ()).throw(Exception("foo")),
    )

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["generate"])

    assert "VENDOR not provided" in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_sheet_image(option, monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN sheet-image is run with given workbook and worksheet
    """
    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_path = os.path.join("foo", "bar")
    expected_msg = (
        f"Creating image enhanced spreadsheet for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"saving Excel file to 'out.xlsx'..."
    )
    monkeypatch.setattr(cli, "sheet_image_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["dir"], "images", expected_path)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["-v", vendor_code, "-b", workbook, option, worksheet, "sheet-image"]
    )

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_sheet_image_no_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a workbook
    AND without a worksheet
    THEN sheet-image is run with given workbook
    """
    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    expected_path = os.path.join("foo", "bar")
    expected_msg = (
        f"Creating image enhanced spreadsheet for '{vendor_code}' "
        f"using '{workbook}':'', "
        f"saving Excel file to 'out.xlsx'..."
    )
    monkeypatch.setattr(cli, "sheet_image_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["dir"], "images", expected_path)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["-v", vendor_code, "-b", workbook, "sheet-image"])

    assert result.exit_code == 0
    assert expected_msg in result.output


def test_mkthumbs(monkeypatch, target_directory):
    """
    GIVEN cli
    WHEN the mkthumbs sub-command is called
    THEN mkthumbs is run
    """
    monkeypatch.setattr(cli, "mkthumbs", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["mkthumbs", "--image-directory", target_directory])

    image_directory = target_directory
    assert result.exit_code == 0
    assert f"Creating thumbnails of images in '{image_directory}'..." in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_order(option, monkeypatch):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN order is run for the given vendor with given workbook
    AND spreadsheet.get_order_items is called
    """
    timeout = "0"
    item_id = "foo"
    qty = "42"
    vendor_code = "gj"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_msg = (
        f"Creating web order for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"Adding items to cart..."
    )

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="mock_scraper")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            option,
            worksheet,
            "order",
            "--timeout",
            timeout,
        ],
    )

    assert result.exit_code == 0
    assert expected_msg in result.output
    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.GJScraper().load_item_page.assert_any_call(item_id)
    mock_scraper.GJScraper().add_to_cart.assert_called_with(qty)


def test_order_without_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND without a worksheet
    THEN order is run for the given vendor with given workbook
    AND spreadsheet.get_order_items is called
    """
    timeout = "0"
    item_id = "foo"
    qty = "42"
    vendor_code = "gj"
    workbook = "myWorkBook"
    expected_msg = (
        f"Creating web order for '{vendor_code}' "
        f"using '{workbook}':'', "
        f"Adding items to cart..."
    )

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="mock_scraper")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            "order",
            "--timeout",
            timeout,
        ],
    )

    assert result.exit_code == 0
    assert expected_msg in result.output
    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.GJScraper().load_item_page.assert_any_call(item_id)
    mock_scraper.GJScraper().add_to_cart.assert_called_with(qty)


def test_order_with_empty_qty(monkeypatch, spreadsheet_filepath):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN order is run
    AND scraper.add_to_car is only called for titles with
    an order quanitity greater than 0.
    """
    vendor_code = "gj"
    workbook = "myWorkBook"
    worksheet = "Sheet1"
    timeout = "0"
    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="GJScraper")
    mock_spreadsheet.get_order_items.return_value = [
        ("foo", 1),
        ("bar", None),
        ("baz", 0),
        ("fred", 2),
    ]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)
    monkeypatch.setattr(
        cli, "get_driver_scraper", lambda vendor, email: (Mock(), mock_scraper)
    )
    mock_scraper.load_item_page.return_value = True
    runner = CliRunner()
    runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            "-s",
            worksheet,
            "order",
            "--timeout",
            timeout,
        ],
    )
    num_titles_with_valid_qty = 2
    assert mock_scraper.add_to_cart.call_count == num_titles_with_valid_qty


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_order_with_email(option, monkeypatch):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    AND an email
    THEN order is run for the given vendor with given workbook and worksheet and email
    AND spreadsheet.get_order_items is called
    """
    timeout = "0"
    item_id = "foo"
    qty = "42"
    email = "foo@example.org"
    vendor_code = "tb"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_msg = (
        f"Creating web order for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"Adding items to cart..."
    )

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="mock_scraper")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            option,
            worksheet,
            "order",
            "--email",
            email,
            "--timeout",
            timeout,
        ],
    )

    assert result.exit_code == 0
    assert expected_msg in result.output
    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.TBScraper().impersonate.assert_called_with(email)
    mock_scraper.TBScraper().add_to_cart.assert_called_with(qty)


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_sheet_waves(option, monkeypatch, target_directory):
    """
    GIVEN cli
    WHEN the sheet-waves sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN sheet-waves is run with given workbook and worksheet
    """
    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_msg = (
        f"Creating waves import spreadsheet for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"saving Excel file to 'out.xlsx'..."
    )
    monkeypatch.setattr(cli, "sheet_waves_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["-v", vendor_code, "-b", workbook, option, worksheet, "sheet-waves"]
    )

    assert result.exit_code == 0
    assert expected_msg in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_update_images_flag(option, monkeypatch):
    """
    GIVEN cli
    WHEN scrape is called with the --update-images flag, a vendor argument
    AND a workbook
    AND a worksheet
    THEN update_images is run with given workbook and worksheet
    """
    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_path = os.path.join("foo", "bar")
    expected_msg = (
        f"Updating image data for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"saving data to '{expected_path}'"
    )
    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            option,
            worksheet,
            "scrape",
            "--update-images",
        ],
    )
    assert result.exit_code == 0
    assert expected_msg in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_scrape_with_update_image_and_update_rank(option, monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called with --update-images
    AND --update-ranks
    THEN the expected msg appears
    """
    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_path = os.path.join("foo", "bar")
    expected_msg = (
        f"Updating image data and re-scraping rank data for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}', "
        f"saving data to '{expected_path}'"
    )
    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            option,
            worksheet,
            "scrape",
            "--update-images",
            "--update-ranks",
        ],
    )
    assert result.exit_code == 0
    assert expected_msg in result.output


def test_sheet_image_with_cutoff_date_flag(monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a cutoff-date
    AND a workbook
    THEN sheet-image is called with the cutoff-date
    """
    out = "out.xlsx"
    vendor_code = "tb"
    workbook = "myWorkBook"
    expected_msg = (
        f"Creating image enhanced spreadsheet for "
        f"'{vendor_code}' "
        f"using '{workbook}':"
        f"'', "
        "with a cutoff date of '01/02/2025'"
        f"saving Excel file to '{out}'..."
    )
    mock_spreadsheet = Mock(name="mock_spreadsheet")

    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            "sheet-image",
            "--cutoff-date",
            "01/02/2025",
        ],
    )
    assert result.exit_code == 0
    assert expected_msg in result.output


@pytest.mark.parametrize("s_option", ("-s", "--worksheet"))
def test_generate_with_html_and_mailchimp_flags_exits(s_option, monkeypatch):
    """
    GIVEN the cli
    WHEN the generate sub-command is called with the html and mailchimp flags
    THEN helpful text is displayed
    """
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    worksheet = "TEST_WORKSHEET"
    expected_msg = (
        "\tHtml flag is not compatable with the Mailchimp flag"
        "\n\tCannot continue.  Exiting."
    )

    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            s_option,
            worksheet,
            "generate",
            "--html",
            "--mailchimp",
        ],
    )
    assert expected_msg in result.output


@pytest.mark.parametrize("s_option", ("-s", "--worksheet"))
@pytest.mark.parametrize("t_option", ("-t", "--title"))
def test_generate_with_mailchimp_flag(s_option, t_option, monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called with the mailchimp flag
    AND a vendor
    AND a sheet_id argument
    AND a worksheet argument
    AND a title argument
    THEN generate is run
    """
    title = "my_campaign"
    vendor_code = "AWESOME_VENDOR"
    workbook = "TEST_SHEET_ID"
    worksheet = "TEST_WORKSHEET"
    expected_msg = (
        f"Creating Mailchimp html content '{title}' for '{vendor_code}' "
        f"using '{workbook}':'{worksheet}'..."
    )

    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "-v",
            vendor_code,
            "-b",
            workbook,
            s_option,
            worksheet,
            "generate",
            "--mailchimp",
            t_option,
            title,
        ],
    )
    # breakpoint()
    assert result.exit_code == 0
    assert expected_msg in result.output
