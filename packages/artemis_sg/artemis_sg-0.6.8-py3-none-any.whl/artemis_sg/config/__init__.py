import logging
import os

from flatten_dict import flatten, unflatten

import artemis_sg

namespace = "artemis_sg.config"

# Everyghing that can be configured is here.
CFG = {
    "asg": {
        "vendors": [
            {
                "code": "sample",
                "name": "Sample Vendor",
                "isbn_key": "ISBN-13",
                "failover_scraper": "",
            },
            {
                "code": "sample2",
                "name": "Another Vendor",
                "isbn_key": "ISBN",
                "failover_scraper": "AmznUkScraper",
            },
        ],
        "item": {
            "sort_order": [
                "TITLE",
                "SUBTITLE",
                "AUTHOR",
                "PUBLISHER",
                "PUB DATE",
                "PUBLISHERDATE",
                "FORMAT",
            ],
        },
        "spreadsheet": {
            "order": {"order_col": "Order"},
            "update_images_from": "Image",
            "sheet_image": {
                "col_order": [
                    "ISBN",
                    "IMAGE",
                    "ORDER",
                ],
                "vendor_date_col_names": {"sample": "Start Date"},
                "image_row_height": 105,
                "image_col_width": 18,
                "isbn_col_width": 13,
                "max_col_width": 50,
                "col_buffer": 1.23,
            },
            "mkthumbs": {
                "width": 130,
                "height": 130,
            },
            "sheet_waves": {
                "qty_col_names": {
                    "sample": {"workbook": "on_hand", "inventory": "quantity"}
                },
                "image_columns": [
                    "Image URL",
                    "Image 1",
                    "Image 2",
                    "Image 3",
                    "Image 4",
                    "Image 5",
                    "Image 6",
                ],
                "data_columns": [
                    "Description",
                    "Width",
                    "Length",
                    "Height",
                    "category_path",
                    "Pound Pricing",
                    "is_private",
                    "product_active",
                ],
                "pound_pricing_map": {
                    "af": {
                        "2": {"99": 1.00},
                        "3": {"50": 1.20, "99": 1.50},
                    },
                    "bf": {
                        "3": {"50": 1.20, "99": 1.50},
                        "4": {"50": 1.60},
                    },
                    "cf": {
                        "3": {"99": 1.50},
                    },
                },
                "pound_pricing_unmapped_multiplier": 0.4,
                "calculate_fields": {
                    "is_private": {
                        "map_from": "Rights",
                        "map": {
                            "R1": 1,
                            "R2": 1,
                            "R3": 1,
                        },
                    },
                    "category_path": {
                        "map_from": ["Format", "Category 1", "Category 2"],
                        "map": {
                            "example format": {
                                "example category 1": {
                                    "example category 2": "example/category/path"
                                }
                            }
                        },
                    },
                },
                "discounted_prices": ["50%", "60%"],
                "discount_text_map": "{t} off (usd)",
                "preset_fields": {
                    "quantity_monitor": 1,
                    "Brand": "66 Books, Ltd.",
                    "dimension_measurement_unit": "inches",
                },
                "rename_fields": {
                    "Barcode": "product_sku",
                    "Title": "Name",
                    "Available Stock": "quantity",
                    "Rights": "Privacy Group",
                    "RRP": "msrp_gbp",
                },
            },
        },
        "scraper": {
            "headless": False,
            "login_timeout": 90,
            "gjscraper": {
                "sentinel_publisher": "Abbeville",
            },
        },
        "data": {
            "file": {
                "scraped": os.path.join(artemis_sg.data_dir, "scraped_items.json"),
            },
            "dir": {
                "images": os.path.join(artemis_sg.data_dir, "downloaded_images"),
                "upload_source": os.path.join(artemis_sg.data_dir, "downloaded_images"),
            },
            "supported_img_formats": [".jpg", ".png"],
        },
        "slide_generator": {
            "html": {
                "font_size": "18px",
                "page_background_color": "#ffe6b3",
                "container_background_color": "#b22424c1",
                "cover_img_max_height": "600px",
                "cover_img_max_width": "300px",
                "suppl_img_height": "100px",
                "suppl_img_width": "100px",
                "max_suppl_images_per_title": 8,
                "max_images_per_column": 4,
                "logo_width": "140px",
                "logo_height": "100px",
                "bold_text": ["TITLE"],
            },
            "title_default": "New Arrivals",
            "line_spacing": 1,
            "text_width": 80,
            "max_fontsize": 18,
            "slide_max_batch": 25,
            "slide_ppi": 96,
            "slide_w": 10.0,
            "slide_h": 5.625,
            "gutter": 0.375,
            "text_box_resize_img_threshold": 2,
            "logo_h": 1,
            "logo_w": 1,
            "addl_img_h": 1.5,
            "addl_img_w": 3,
            "logo_url": "https://images.squarespace-cdn.com/content/v1/6110970ca45ca157a1e98b76/e4ea0607-01c0-40e0-a7c0-b56563b67bef/artemis.png?format=1500w",
            "blacklist_keys": (
                "IMAGE",
                "ON HAND",
                "ORDER",
                "ORDER QTY",
                "GJB SUGGESTED",
                "DATE RECEIVED",
                "SUBJECT",
                "QTYINSTOCK",
                "QTY",
                "SALESPRICE",
                "AVAILABLE START DATE",
                "CATEGORY",
                "LINK",
            ),
            "gj_binding_map": {
                "P": "Paperback",
                "H": "Hardcover",
                "C": "Hardcover",
                "C NDJ": "Cloth, no dust jacket",
                "CD": "CD",
            },
            "gj_type_map": {"R": "Remainder", "H": "Return"},
            "bg_color": "black",
            "text_color": "white",
            "tiny_isbn_x_inset": 1.0,
            "tiny_isbn_fontsize": 6,
            "text_box_max_lines": 36,
            "text_box_resized_max_lines": 28,
            "text_map": {
                "prices": {
                    "YOUR COST": "Your Cost: ${t}",
                    "PUB LIST": "List Price: ${t}",
                    "LISTPRICE": "List Price: ${t}",
                    "LIST PRICE": "List Price: ${t}",
                    "USD COST": "USD Cost: ${t}",
                    "RRP": "List price: £{t}",
                    "BARGAIN": "Bargain: £{t}",
                    "NET COST": "Your Net Price: ${t}",
                    "YOUR NET PRICE": "Your Net Price: ${t}",
                    "COVER PRICE": "Cover Price: £{t}",
                },
                "sample": {
                    "ISBN": "www.sample_vendor_specific_text_map/{t}",
                },
                "AUTHOR": "by {t}",
                "PUB DATE": "Pub Date: {t}",
                "PUBLISHERDATE": "Pub Date: {t}",
                "BINDING": "Format: {t}",
                "FORMAT": "Format: {t}",
                "TYPE": "Type: {t}",
                "PAGES": "Pages: {t} pp.",
                "SIZE": "Size: {t}",
                "ITEM#": "Item #: {t}",
                "TBCODE": "Item #: {t}",
                "AMAZON": "Amazon Ranking: #{t}",
                "AMAZON_UK": "Amazon UK Ranking: #{t}",
            },
        },
        "test": {
            "sheet": {"id": "GOOGLE_SHEET_ID_HERE", "tab": "GOOGLE_SHEET_TAB_HERE"}
        },
    },
    "google": {
        "cloud": {
            "new_threshold_secs": 3600,
            "bucket": "my_bucket",
            "bucket_prefix": "my_bucket_prefix",
            "public_html_bucket": "my_public_html_bucket",
            "key_file": os.path.join(
                artemis_sg.data_dir, "google_cloud_service_key.json"
            ),
        },
        "docs": {
            "api_creds_file": os.path.join(artemis_sg.data_dir, "credentials.json"),
            "api_creds_token": os.path.join(
                artemis_sg.data_dir, "app_creds_token.json"
            ),
        },
    },
}

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

conf_file = "config.toml"

conf_path = os.path.join(artemis_sg.conf_dir, conf_file)

try:
    with open(conf_path, mode="rb") as fp:
        f_config = tomllib.load(fp)
except FileNotFoundError:
    import tomli_w

    logging.warning(f"{namespace}: Config file not found at {conf_path}.")
    logging.warning(f"{namespace}: Creating new config file at {conf_path}.")
    logging.warning(
        f"{namespace}: IMPORTANT: Edit file to set proper values for google_cloud."
    )

    d = os.path.dirname(conf_path)
    if not os.path.exists(d):
        os.makedirs(d)
    with open(conf_path, mode="wb") as fp:
        tomli_w.dump(CFG, fp)
    with open(conf_path, mode="rb") as fp:
        f_config = tomllib.load(fp)

# Update CFG with contents of f_config
flat_cfg = flatten(CFG)
flat_f_config = flatten(f_config)
flat_merged = flat_cfg | flat_f_config
CFG = unflatten(flat_merged)

# Create all defined data_dir subdirectories
for key in CFG["asg"]["data"]["dir"]:
    d = CFG["asg"]["data"]["dir"][key]
    if not os.path.exists(d):
        logging.warning(f"{namespace}: Creating new directory at {d}.")
        os.makedirs(d)

# Create all defined data_dir files
for key in CFG["asg"]["data"]["file"]:
    f = CFG["asg"]["data"]["file"][key]
    if not os.path.exists(f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            logging.warning(f"{namespace}: Creating new directory at {d}.")
            os.makedirs(d)
        logging.warning(f"{namespace}: Creating new file at {f}.")
        _root, ext = os.path.splitext(f)
        with open(f, "w") as fp:
            # Seed JSON files with valid empty JSON.
            if ext.lower() == ".json":
                fp.write("{ }")
            pass
