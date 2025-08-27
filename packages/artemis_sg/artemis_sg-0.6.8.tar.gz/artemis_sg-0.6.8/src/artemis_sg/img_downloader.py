#!/usr/bin/env python
# ruff: noqa: PLC0206
"""artemis_sg.img_downloader

Downloads images from URLs in scraped data."""

import json
import logging
import os
import sysconfig
import tempfile

import puremagic
import requests
from rich.console import Console
from rich.text import Text

from artemis_sg.config import CFG
from artemis_sg.isbn import validate_isbn
from artemis_sg.items import Items
from artemis_sg.spreadsheet import get_sheet_data
from artemis_sg.vendor import vendor

MODULE = os.path.splitext(os.path.basename(__file__))[0]
console = Console()
supported_img_formats = CFG["asg"]["data"]["supported_img_formats"]


class ImgDownloader:
    """
    Object that downloads images from URLs in data.

    """

    def get_image_ext(self, path: str) -> str:
        """
        Get file extension of image file from given path,
        empty string if not valid image type.

        :param path: Path of file.
        :returns: Image file extension.
        """
        namespace = f"{type(self).__name__}.{self.get_image_ext.__name__}"

        try:
            possible_kind = puremagic.from_file(path)
        except (puremagic.main.PureError, ValueError):
            logging.warning(f"{namespace}: non-image file found")
            possible_kind = ""

        kind = possible_kind if possible_kind in supported_img_formats else ""
        return kind

    def download(self, image_dict: dict[str, list[str]], target_dir: str = "") -> str:
        """
        Download image from URL in dictionary list values and save to target_dir.

        :param image_dict: Dictionary with ISBN keys and image url list values.
        :param target_dir: Directory to save file to.
        :returns: Path of downloaded file.
        """
        namespace = f"{type(self).__name__}.{self.download.__name__}"

        if not target_dir:
            target_dir = tempfile.mkdtemp(prefix="ImgDownloader-")
            logging.warning(f"{namespace}: Creating target directory at {target_dir}")
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        for key in image_dict:
            for i, url in enumerate(image_dict[key]):
                isbn = validate_isbn(key)
                if not isbn:
                    isbn = key
                suffix = "" if i == 0 else f"-{i}"
                image = f"{isbn}{suffix}.jpg"
                image_path = os.path.join(target_dir, image)
                try:
                    self._download_url(url, image_path, isbn)
                except Exception as e:
                    logging.exception(f"{namespace}: Error occured: '{e}'")

        return target_dir

    def _download_url(self, url, image_path, isbn):
        namespace = f"{type(self).__name__}.{self._download_url.__name__}"
        log_prefix = f"{namespace}: ISBN {isbn}, "
        if not hasattr(self, "tried_get_pem"):
            self.tried_get_pem = False
        res = True
        if not os.path.isfile(image_path) or not self.get_image_ext(image_path):
            logging.debug(f"{log_prefix}downloading '{url}' to '{image_path}'")
            try:
                r = requests.get(url, timeout=10)
            except requests.exceptions.SSLError as e:
                if not self.tried_get_pem:
                    self.get_pem()
                    self.tried_get_pem = True
                else:
                    logging.warning(
                        f"{log_prefix}failed to retrieve '{url}'. Error: '{e}',"
                    )
                    raise e
            except ConnectionError as e:
                logging.warning(
                    f"{log_prefix}failed to retrieve '{url}'. Error: '{e}',"
                )
                raise e

            with open(image_path, "wb") as fp:
                fp.write(r.content)

            # validate file and name it in accordance with its type
            fmt = self.get_image_ext(image_path)
            file_ext = os.path.splitext(image_path)[1]
            if fmt not in supported_img_formats:
                os.remove(image_path)
                logging.warning(
                    f"{log_prefix}Skipping unsupported file type in '{url}'"
                )
                res = False
            elif fmt != file_ext:
                old_path = image_path
                image_path = os.path.splitext(old_path)[0] + fmt
                if os.path.isfile(image_path):
                    logging.warning(
                        f"{log_prefix}Overwriting existing file '{image_path}'."
                    )
                    os.remove(image_path)
                os.rename(old_path, image_path)

            return res

    def get_pem(self):
        r = requests.get(
            (
                "https://gitlab.com/johnduarte/artemis_sg/uploads/"
                "422a7296bb6b92fdd6cc69bfaf07eb8c/www-texasbookman-com.pem"
            ),
            timeout=10,
        )
        pem_file = os.path.join(
            sysconfig.get_paths()["purelib"], "certifi", "cacert.pem"
        )
        with open(pem_file, "a") as fp:
            fp.write(r.text)

        return r.text

    def get_image_url_dict(self, data, isbns=None):
        # TODO:  This seems like duplication of Items code.
        #        However, the Items instance interface is clunky in this
        #        context since sheet data is not available for mapping.
        #        If isbns is specified, then only those are added to the url_dict.
        url_dict = {}
        if isbns:  # only get images from isbn list
            for isbn in isbns:
                try:
                    url_dict[isbn] = data[f"{isbn}"]["image_urls"]
                    logging.debug(f"found isbn: {isbn}")
                except KeyError:
                    logging.debug(f"could not find isbn in database: {isbn}")
            return url_dict
        # get all images
        for key in data:
            url_dict[key] = data[key]["image_urls"]
        return url_dict


def main(vendor_code=None, workbook=None, worksheet=None):
    """Download images from URLs in datafile.

    Using the configured [asg.data.file.scraped] datafile, URLs within
    are downloaded to the configured [asg.data.dir.images] directory.
    """
    scraped_datafile = CFG["asg"]["data"]["file"]["scraped"]
    saved_images_dir = CFG["asg"]["data"]["dir"]["images"]
    if not os.path.isdir(saved_images_dir):
        dest = None

    dloader = ImgDownloader()

    def get_json_data_from_file(datafile):
        # TODO:  This seems like duplication of Items.load_scraped_data.
        #        However, the Items instance interface is clunky in this
        #        context since sheet data is not available for mapping.
        namespace = f"{MODULE}.main.{get_json_data_from_file.__name__}"
        try:
            with open(datafile) as filepointer:
                data = json.load(filepointer)
            filepointer.close()
            return data
        except FileNotFoundError:
            logging.error(f"{namespace}: Datafile '{datafile}' not found")
            return {}
        except json.decoder.JSONDecodeError:
            logging.error(
                f"{namespace}: Datafile '{datafile}' did not contain valid JSON"
            )
            return {}

    if vendor_code is not None and workbook is not None:  # only download from the keys
        isbn_key = vendor(vendor_code).isbn_key
        logging.debug(f"Setting ISBN_KEY to '{isbn_key}'.")
        sheet_data = get_sheet_data(workbook, worksheet)
        sheet_keys = [x for x in sheet_data.pop(0) if x]
        items = Items(sheet_keys, sheet_data, isbn_key)
        isbns = [item.isbn for item in items]
    else:
        isbns = None

    scraped_data = get_json_data_from_file(scraped_datafile)
    img_dict = dloader.get_image_url_dict(scraped_data, isbns)
    dest = dloader.download(img_dict, saved_images_dir)
    dest_text = Text(f"Images downloaded to {dest}.")
    dest_text.stylize("green")
    console.print(dest_text)


if __name__ == "__main__":
    main()
