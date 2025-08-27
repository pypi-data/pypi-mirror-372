#!/usr/bin/env python

import datetime
import logging
import os
import sys
from time import sleep

import click
from rich.console import Console
from rich.progress import track
from rich.text import Text
from selenium.common.exceptions import NoSuchWindowException

from artemis_sg import gcloud, img_downloader, scraper, slide_generator, spreadsheet
from artemis_sg.config import CFG

MODULE = os.path.splitext(os.path.basename(__file__))[0]
console = Console()

v_skip = "{}: skipping due to lack of VENDOR"
b_skip = "{}: skipping due to lack of WORKBOOK"


@click.group(chain=True)
@click.option("-V", "--verbose", is_flag=True, help="enable verbose mode")
@click.option("-D", "--debug", is_flag=True, help="enable debug mode")
@click.option("-L", "--logfile", is_flag=True, help="log to file")
@click.option("-v", "--vendor", default=None, help="Vendor code")
@click.option(
    "-b", "--workbook", default=None, help="Workbook (Sheets Doc ID or Excel File)"
)
@click.option("-s", "--worksheet", default=None, help="Worksheet within Sheets Doc")
@click.pass_context
def cli(ctx, verbose, debug, logfile, vendor, workbook, worksheet):  # noqa: PLR0913
    """artemis_sg is a tool for processing product spreadsheet data.
    Its subcommands are designed to be used to facilitate the follow primary
    endpoint conditions:

    \b
    * A Google Slide Deck of products
    * An enhanced Excel spreadsheet
    * A website order

    The subcommands can be combined into desired workflows.

    The base command includes --vendor, --workbook, and --worksheet options.
    These are used to pass context information to the subcommands.  Some
    subcommands expect --vendor and --workbook values to perform as designed.

    Example of Google Slide Deck workflow:

        $ artemis_sg -v sample -b tests/data/test_sheet.xlsx \\
                scrape download upload generate -t "Cool Deck"

    Example of Sheet Image workflow:

        $ artemis_sg -v sample -b tests/data/test_sheet.xlsx \\
                scrape download mkthumbs sheet-image -o "NewFile.xlsx"
    """
    namespace = f"{MODULE}.cli"
    logargs = {
        "format": "%(asctime)s %(levelname)-8s %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
    if logfile:
        dt = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d-%H%M%S")
        logfile_name = f"artemis_sg-{dt}.log"
        logargs = {**logargs, "filename": logfile_name, "filemode": "w"}
    if debug:
        logargs = {**logargs, "level": logging.DEBUG}
        logging.basicConfig(**logargs)
        logging.debug(f"{namespace}: Debug mode enabled.")

    elif verbose:
        logargs = {**logargs, "level": logging.INFO}
        logging.basicConfig(**logargs)
        logging.info(f"{namespace}: Verbose mode enabled.")
    else:
        logging.basicConfig(**logargs)

    # load up context object (ctx)
    ctx.ensure_object(dict)
    ctx.obj["VENDOR"] = vendor
    ctx.obj["WORKBOOK"] = workbook
    ctx.obj["WORKSHEET"] = worksheet


@cli.command()
@click.option(
    "--update-images",
    is_flag=True,
    help="Update existing titles with images from a spreadsheet",
)
@click.option(
    "--update-ranks",
    is_flag=True,
    help="Scrape existing titles for rank",
)
@click.pass_context
def scrape(ctx, update_images, update_ranks):
    """Scrape web data for vendor from workbook:worksheet

    Iterates over the item rows in the spreadsheet provided by the
    --workbook:--worksheet values passed by the base command.  The ISBN field
    is idenfied by the --vendor value passed by the base command.  For each
    ISBN in the WORKBOOK:WORKSHEET, it searches for item descriptions and
    images in a web browser.  It collects this information and stores it in the
    file defined by the configuration field [asg.data.file.scraped].  If data
    for an ISBN already exists in the datafile, the ISBN is skipped and does
    not result in re-scraping data for that record.

    Scrape supports both Google Sheet ID and Excel file paths for the WORKBOOK
    value.

    If a --worksheet is not defined, the first sheet in the WORKBOOK will be
    used.  If the given WORKBOOK contains multiple sheets and the sheet
    containing the desired data is not the first sheet in the WORKBOOK, the
    --worksheet will need to be specified for the base command.

    The command utilizes configuration variables stored in "config.toml" to set
    the vendor from [asg.vendors] and scraped items database from
    [asg.data.file.scraped].
    """
    cmd = "scrape"
    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            sdb = CFG["asg"]["data"]["file"]["scraped"]
            if update_images and update_ranks:
                action = "Updating image data and re-scraping rank data"
            elif update_images:
                action = "Updating image data"
            elif update_ranks:
                action = "Re-scraping rank data"
            else:
                action = "Scraping web data"
            msg = (
                f"{action} for '{ctx.obj['VENDOR'] or ''!s}' "
                f"using '{ctx.obj['WORKBOOK'] or ''!s}':"
                f"'{ctx.obj['WORKSHEET'] or ''!s}', "
                f"saving data to '{sdb}'..."
            )
            click.echo(msg)
            scraper_wrapper(
                ctx.obj["VENDOR"],
                ctx.obj["WORKBOOK"],
                ctx.obj["WORKSHEET"],
                sdb,
                update_images,
                update_ranks,
            )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


@cli.command()
@click.pass_context
def download(ctx):
    """
    Download scraped images

    Iterates over the data records in the file defined by the configuration
    field [asg.data.file.scraped].  For each record, it downloads the image
    files associated with the record to a local directory as defined by the
    configuration field [asg.data.dir.images]. If a workbook and vendor is
    specified, only titles included in the workbook will be downloaded.
    """
    namespace = f"{MODULE}.download"
    if ctx.obj["VENDOR"] and ctx.obj["WORKBOOK"]:
        msg = (
            f"Downloading images for titles from '{ctx.obj['VENDOR'] or ''!s}' "
            f"using '{ctx.obj['WORKBOOK'] or ''!s}':"
            f"'{ctx.obj['WORKSHEET'] or ''!s}', "
        )
    else:
        msg = "Downloading images..."
    download_path = CFG["asg"]["data"]["dir"]["images"]
    click.echo(msg)
    logging.debug(f"{namespace}: Download path is: {download_path}")

    img_downloader_wrapper(ctx.obj["VENDOR"], ctx.obj["WORKBOOK"], ctx.obj["WORKSHEET"])


@cli.command()
def upload():
    """
    Upload local images to Google Cloud Storage Bucket

    Uploads the files in the directory defined by the configuration field
    [asg.data.dir.upload_source] to the Google Cloud bucket defined by the
    configuration field [google.cloud.bucket].  Only the first level of the
    source directory is uploaded.  Subdirectories of the source directory are
    not traversed for the upload.  All uploaded files are prefixed with value
    defined by the configuration field [google.cloud.bucket_prefix].
    """
    namespace = f"{MODULE}.upload"

    upload_source = CFG["asg"]["data"]["dir"]["upload_source"]
    click.echo("Uploading images to Google Cloud...")
    logging.debug(f"{namespace}: Upload source path is: {upload_source}")

    gcloud_wrapper()


@cli.command()
@click.option(
    "-t",
    "--title",
    default=CFG["asg"]["slide_generator"]["title_default"],
    help="Slide deck title",
)
@click.option("--html", is_flag=True, help="Generate with HTML")
@click.option(
    "--mailchimp", is_flag=True, help="Generate HTML for a Mailchimp content block"
)
@click.pass_context
def generate(ctx, title, html, mailchimp):
    """
    Generate a Google Slide Deck


    The slide deck will be given a title based on the values supplied by VENDOR
    and --title.  The title slide will be in the following format:

        Artemis Book Sales Presents...
        Vendor Name, Title

    Iterates over item rows in the spreadsheet provided by the
    --workbook:--worksheet values passed by the base command.  The ISBN field
    is idenfied by the --vendor value passed by the base command.  For each
    ISBN in the WORKBOOK:WORKSHEET
    for which it has image data it creates a slide containing the
    spreadsheet data, the description saved in the file defined by the configuration
    field [asg.data.file.scraped], and the images saved in the
    [google.cloud.bucket].  The Google sheet will be saved to the root of the
    Google Drive associated with the credentials created during initial
    installation.

    Generate supports both Google Sheet ID and Excel file paths for the WORKBOOK
    value.

    If a --worksheet is not defined, the first sheet in the WORKBOOK will be
    used.  If the given WORKBOOK contains multiple sheets and the sheet
    containing the desired data is not the first sheet in the WORKBOOK, the
    --worksheet will need to be specified for the base command.

    The command utilizes configuration variables stored in "config.toml" to set
    the vendor from [asg.vendors] and scraped items database from
    [asg.data.file.scraped].
    """
    cmd = "generate"
    namespace = f"{MODULE}.{cmd}"

    if not ctx.obj["VENDOR"]:
        click.echo("\tVENDOR not provided", err=True)
        click.echo("\tCannot continue.  Exiting.", err=True)
        sys.exit(1)
    if not ctx.obj["WORKBOOK"]:
        click.echo("\tWORKBOOK not provided", err=True)
        click.echo("\tCannot continue.  Exiting.", err=True)
        sys.exit(1)
    if html and mailchimp:
        click.echo("\tHtml flag is not compatable with the Mailchimp flag", err=True)
        click.echo("\tCannot continue.  Exiting.", err=True)
        sys.exit(1)
    sdb = CFG["asg"]["data"]["file"]["scraped"]
    if html:
        gen_method = "html deck"
    elif mailchimp:
        gen_method = "Mailchimp html content"
    else:
        gen_method = "Google Slides deck"
    msg = (
        f"Creating {gen_method} '{title}' for '{ctx.obj['VENDOR'] or ''!s}' "
        f"using '{ctx.obj['WORKBOOK'] or ''!s}':'{ctx.obj['WORKSHEET'] or ''!s}'..."
    )
    click.echo(msg)
    logging.debug(f"{namespace}: Scraped Items Database is: {sdb}")
    flags = {"html": html, "mailchimp": mailchimp}
    slide_generator_wrapper(
        ctx.obj["VENDOR"], ctx.obj["WORKBOOK"], ctx.obj["WORKSHEET"], sdb, title, flags
    )


@cli.command()
@click.option("-o", "--output", "out", default="out.xlsx", help="Output file")
@click.option(
    "--cutoff-date",
    help="Only adds images for titles after the cutoff date",
    default=None,
)
@click.pass_context
def sheet_image(ctx, out, cutoff_date):
    """
    Insert item thumbnail images into spreadsheet

    Iterates over item rows in the spreadsheet provided by the
    --workbook:--worksheet values passed by the base command.  The ISBN field
    is idenfied by the --vendor value passed by the base command.  For each

    Modifies a local XLSX spreadsheet file provided by the
    --workbook:--worksheet values passed by the base command to include
    thumbnail images in the second column for ISBN items (field itentified by
    --vendor) in which local thumbnail image files are available and saves a
    new XLSX file.

    By default, the thumbnail images are obtained from
    [asg.data.dir.images]/thumbnails and the new XLSX file is saved as
    "out.xlsx" in the current working directory.

    NOTE: Currently, the command does not support Google Sheet IDs as a valid
    WORKBOOK type.

    If a --worksheet is not defined, the first sheet in the WORKBOOK will be
    used.  If the given WORKBOOK contains multiple sheets and the sheet
    containing the desired data is not the first sheet in the WORKBOOK, the
    --worksheet will need to be specified for the base command.

    The command utilizes configuration variables stored in "config.toml" to set
    the vendor from [asg.vendors].
    """
    cmd = "sheet-image"
    namespace = f"{MODULE}.sheet_image"

    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            download_path = CFG["asg"]["data"]["dir"]["images"]
            image_directory = os.path.join(download_path, "thumbnails")
            cutoff_msg = f"with a cutoff date of '{cutoff_date}'" if cutoff_date else ""
            msg = (
                f"Creating image enhanced spreadsheet for "
                f"'{ctx.obj['VENDOR'] or ''!s}' "
                f"using '{ctx.obj['WORKBOOK'] or ''!s}':"
                f"'{ctx.obj['WORKSHEET'] or ''!s}', "
                f"{cutoff_msg}"
                f"saving Excel file to '{out}'..."
            )
            click.echo(msg)
            logging.debug(
                f"{namespace}: Thumbnail Image Directory is: {image_directory}"
            )
            options = {"out": out, "cutoff_date": cutoff_date}
            sheet_image_wrapper(
                ctx.obj["VENDOR"],
                ctx.obj["WORKBOOK"],
                ctx.obj["WORKSHEET"],
                image_directory,
                options,
            )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


@cli.command()
@click.option("-o", "--output", "out", default="out.xlsx", help="Output file")
@click.option(
    "--gbp_to_usd",
    help="Specify a GBP to USD conversion rate to be applied to the discounted prices",
    default=None,
)
@click.option(
    "--inventory",
    help="Specify an inventory list to update quantity with",
    default=None,
)
@click.pass_context
def sheet_waves(ctx, out, gbp_to_usd, inventory):
    """
    Insert data columns into spreadsheet

    \b
    * Description
    * Dimension
    * ImageURL0-6

    Modifies a local XLSX spreadsheet file provided by the
    --workbook:--worksheet values passed by the base command to include
    additional columns for ISBN items (field identified by
    --vendor) and saves a
    new XLSX file.

    Iterates over item rows in the spreadsheet provided by the
    --workbook:--worksheet values passed by the base command.  The ISBN field
    is identified by the --vendor value passed by the base command.  For each,
    values are inserted into the added spreadsheet columns

    By default, the new XLSX file is saved as "out.xlsx" in the current working
    directory.

    NOTE: Currently, the command does not support Google Sheet IDs as a valid
    WORKBOOK type.

    If a --worksheet is not defined, the first sheet in the WORKBOOK will be
    used.  If the given WORKBOOK contains multiple sheets and the sheet
    containing the desired data is not the first sheet in the WORKBOOK, the
    --worksheet will need to be specified for the base command.

    The command utilizes configuration variables stored in "config.toml" to set
    the vendor from [asg.vendors].
    """
    if gbp_to_usd:
        try:
            gbp_to_usd = float(gbp_to_usd)
        except ValueError:
            logging.error(f"Invalid GBP to USD conversion rate of: {gbp_to_usd}")
            logging.error("Expected value: Number")
            sys.exit(1)
    cmd = "sheet-waves"
    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            msg = (
                f"Creating waves import spreadsheet for "
                f"'{ctx.obj['VENDOR'] or ''!s}' "
                f"using '{ctx.obj['WORKBOOK'] or ''!s}':"
                f"'{ctx.obj['WORKSHEET'] or ''!s}', "
                f"saving Excel file to '{out}'..."
            )
            click.echo(msg)

            sdb = CFG["asg"]["data"]["file"]["scraped"]
            options = {"out": out, "gbp_to_usd": gbp_to_usd, "inventory": inventory}
            sheet_waves_wrapper(
                ctx.obj["VENDOR"],
                ctx.obj["WORKBOOK"],
                ctx.obj["WORKSHEET"],
                sdb,
                options,
            )
            if gbp_to_usd:
                click.echo(
                    f"Calculated with a GBP to USD conversion rate of {gbp_to_usd}"
                )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


@cli.command()
@click.option(
    "--image-directory",
    default=CFG["asg"]["data"]["dir"]["images"],
    help="Image directory",
)
def mkthumbs(image_directory):
    """
    Create thumbnails of images in IMAGE_DIRECTORY

    Creates thumbnail images from images located in a given directory.  These
    thumbnail images are saved to a "thumbnails" subdirectory in the original
    image directory.  These files are given the same names as their originals.

    By default, the command will use the directory defined by the configuration
    field [asg.data.dir.images] and size them to the dimensions defined by
    [asg.spreadsheet.mkthumbs.width] and [asg.spreadsheet.mkthumbs.height].
    """
    namespace = f"{MODULE}.mkthumbs"

    click.echo(f"Creating thumbnails of images in '{image_directory}'...")
    logging.debug(f"{namespace}: Image Directory is: {image_directory}")

    mkthumbs_wrapper(image_directory)


@cli.command()
@click.option("--email", "email", default="", help="TB Customer email to impersonate")
@click.option(
    "--timeout", "timeout", default="600", help="Maximum time to hold browser open"
)
@click.pass_context
def order(ctx, email, timeout):
    """
    Add items to be ordered to website cart of vendor from spreadsheet

    Populates the website cart for a given --vendor with items from a
    --workbook:--worksheet.  The WORKSHEET MUST contain an "Order" column from
    which the command will get the quantity of each item to put into the cart.

    The browser instance with the populated cart is left open for the user to
    review and manually complete the order.  The user will be asked to manually
    login during the execution of this command.

    NOTE: Currently, this command does not support Google Sheet IDs as a valid
    WORKBOOK type.

    If a --worksheet is not defined, the first sheet in the WORKBOOK will be
    used.  If the given WORKBOOK contains multiple sheets and the sheet
    containing the desired data is not the first sheet in the WORKBOOK, the
    --worksheet will need to be specified for the base command.

    NOTE: The browser opened by this command is controlled by this command.
    The browser will automatically close and the session will be terminated at
    the end of the defined waiting period.  If the web order has not been
    completed by the end of the waiting period, the cart may be lost depending
    on how the website handles its session data.

    The command utilizes configuration variables stored in "config.toml" to set
    the vendor from [asg.vendors].
    """
    cmd = "order"
    timeout = int(timeout)
    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            msg = (
                f"Creating web order for '{ctx.obj['VENDOR'] or ''!s}' "
                f"using '{ctx.obj['WORKBOOK'] or ''!s}':"
                f"'{ctx.obj['WORKSHEET'] or ''!s}', "
                f"Adding items to cart..."
            )
            click.echo(msg)

            order_wrapper(
                email,
                ctx.obj["VENDOR"],
                ctx.obj["WORKBOOK"],
                ctx.obj["WORKSHEET"],
                timeout,
            )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


# wrappers to make the cli testable
def slide_generator_wrapper(vendor, sheet_id, worksheet, sdb, title, flags):
    slide_generator.main(vendor, sheet_id, worksheet, sdb, title, flags)


def gcloud_wrapper():
    gcloud.main()


def img_downloader_wrapper(vendor, workbook, worksheet):
    img_downloader.main(vendor, workbook, worksheet)


def scraper_wrapper(vendor, sheet_id, worksheet, sdb, update_images, update_ranks):
    scraper.main(vendor, sheet_id, worksheet, sdb, update_images, update_ranks)


def sheet_image_wrapper(vendor, workbook, worksheet, image_directory, options):
    spreadsheet.sheet_image(vendor, workbook, worksheet, image_directory, options)


def mkthumbs_wrapper(image_directory):
    spreadsheet.mkthumbs(image_directory)


def order_wrapper(email, vendor, workbook, worksheet, timeout=600):
    order_items = spreadsheet.get_order_items(vendor, workbook, worksheet)
    driver, scrapr = get_driver_scraper(vendor, email)
    if scrapr:
        scrapr.load_login_page()
        scrapr.login()
        if vendor == "tb":
            scrapr.impersonate(email)
        for item, qty in order_items:
            if not qty:
                continue
            if vendor == "tb":
                item_num = scrapr.search_item_num(item)
                if not item_num:
                    continue
            else:
                item_num = item
            res = scrapr.load_item_page(item_num)
            if res:
                scrapr.add_to_cart(qty)
        scrapr.load_cart_page()
        input_text = Text(
            """
        ********    USER INPUT REQUIRED    ********
        Locate the selenium controlled browser
        and manually review and complete your order.
        ********  WAITING FOR USER INPUT   ********
        """
        )
        input_text.stylize("bold cyan")
        console.print(input_text)
        warn_text = Text(
            f"WARNING:  The browser session will terminate in {timeout} seconds!!!!"
        )
        warn_text.stylize("bold red")
        console.print(warn_text)
        for _i in track(
            range(timeout), description="[red]COUNTING DOWN TIME REMAINING..."
        ):
            if not is_browser_alive(driver):
                break
            sleep(1)
    else:
        logging.error(
            f"order: VENDOR '{vendor}' is not supported by the order command."
        )
        sys.exit(1)


def sheet_waves_wrapper(vendor, workbook, worksheet, scraped_items_db, options):
    spreadsheet.sheet_waves(
        vendor,
        workbook,
        worksheet,
        scraped_items_db,
        options,
        **CFG["asg"]["spreadsheet"]["sheet_waves"],
    )


def get_driver_scraper(vendor, email=None):
    if vendor == "tb":
        if not email:
            logging.error(
                f"order: VENDOR '{vendor}' requires the '--email' option to be set."
            )
            sys.exit(1)
        driver = scraper.get_driver()
        scrapr = scraper.TBScraper(driver)
    elif vendor == "gj":
        driver = scraper.get_driver()
        scrapr = scraper.GJScraper(driver)
    elif vendor == "sd":
        driver = scraper.get_driver()
        scrapr = scraper.SDScraper(driver)
    else:
        driver = scrapr = None
    return driver, scrapr


def is_browser_alive(driver):
    try:
        url = driver.current_url
        if url:
            return True
    except (AttributeError, NoSuchWindowException):
        return False


if __name__ == "__main__":
    cli()
