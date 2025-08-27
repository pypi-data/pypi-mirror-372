import datetime
import importlib.resources
import logging
import math
import os
import re
import sys
import textwrap

from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from PIL import Image, ImageColor, ImageDraw, ImageFont
from rich.console import Console
from rich.text import Text

import artemis_sg
import artemis_sg.data
from artemis_sg import spreadsheet
from artemis_sg.app_creds import app_creds
from artemis_sg.config import CFG
from artemis_sg.gcloud import GCloud
from artemis_sg.items import Items
from artemis_sg.vendor import vendor

console = Console()


class SlideGenerator:
    def gj_binding_map(self, code):
        code = code.upper()
        return CFG["asg"]["slide_generator"]["gj_binding_map"].get(code, code)

    def gj_type_map(self, code):
        code = code.upper()
        return CFG["asg"]["slide_generator"]["gj_type_map"].get(code, code)

    def get_slide_text_key_map(self, key, val, item):
        if key in CFG["asg"]["slide_generator"]["text_map"]["prices"]:
            if val is None:
                t = ""
            else:
                try:
                    t = f"{float(val):.2f}"
                except ValueError:
                    t = str(val)
        else:
            t = str(val)
        # hacky exceptions
        if key == "BINDING":
            t = self.gj_binding_map(t)
        if key == "TYPE":
            t = self.gj_type_map(t)
        try:
            fstr = CFG["asg"]["slide_generator"]["text_map"]["prices"][key]
        except KeyError:
            try:
                fstr = CFG["asg"]["slide_generator"]["text_map"][key]
            except KeyError:
                fstr = "ISBN: {t}" if key == item.isbn_key else key.title() + ": {t}"
        # remove quotes and '=' from isbn or ITEM# if needed
        if key == item.isbn_key:
            t = item.isbn  # use validated isbn
        if key == "ITEM#":
            t = match.group(1) if (match := re.search(r"=\"([^\"]+)\"", t)) else t
        return fstr.format(t=t)

    def get_vendor_specific_slide_text_key_map(self, key, item, vendr):
        t = str(item.data[key])
        try:
            fstr = CFG["asg"]["slide_generator"]["text_map"][vendr.code][key]
        except KeyError:
            return None
        return fstr.format(t=t)


class HtmlSlideGenerator(SlideGenerator):
    def __init__(self, gcloud, vendr, template, title) -> None:
        self.validate_filename(title)
        self.title = title
        self.gcloud = gcloud
        self.vendr = vendr
        with open(template, encoding="utf-8") as template_file:
            self.html = BeautifulSoup(template_file, "html.parser")

    def generate(self, items):
        """
        Create an html file for a list of titles.
        """
        self.update_style()
        title_tag = self.tag("title", self.title, None)
        self.html.title.replace_with(title_tag)
        logo_src = CFG["asg"]["slide_generator"]["logo_url"]
        logo = self.tag("img", None, {"class": "logo", "src": logo_src})
        self.html.append(logo)
        for page_num, item in enumerate(items):
            book_container = self.tag("div", None, {"class": "book_container"})
            book_container = self.add_images(book_container, item)
            page_num_div = self.tag("div", f"{page_num + 1}", {"class": "page_number"})
            book_container.append(page_num_div)
            text_div = self.tag("div", None, {"class": "suppl_text"})
            for text in item.data:
                key = text.strip().upper()
                if key in CFG["asg"]["slide_generator"]["blacklist_keys"]:
                    continue
                if isinstance(item.data[text], dict):
                    for subkey in item.data[text]:
                        key = subkey.strip().upper()
                        if key in CFG["asg"]["slide_generator"]["blacklist_keys"]:
                            continue
                        text_tag = self.get_text_tag(key, item.data[text][subkey], item)
                        text_div.append(text_tag)
                else:
                    text_tag = self.get_text_tag(key, item.data[key], item)
                    text_div.append(text_tag)

                    vendor_mapped_val = self.get_vendor_specific_slide_text_key_map(
                        key, item, self.vendr
                    )
                    if vendor_mapped_val:
                        text_tag = self.tag("p", vendor_mapped_val, None)
                        text_div.append(text_tag)

            book_container.append(text_div)
            self.html.append(book_container)
        self.html = self.html.prettify()
        new_filename = f"{self.title}.html"
        with open(new_filename, "w", encoding="utf-8") as f:
            f.write(str(self.html))
        url = self.upload(new_filename)
        os.remove(new_filename)
        return url

    def upload(self, src_path):
        path, file = os.path.split(src_path)
        filename = file.split(".")[0]
        base_url = "https://storage.googleapis.com/"
        current_file_blobs = self.gcloud.list_blobs("")
        current_files = [file.name for file in current_file_blobs]
        cnt = 1
        while file in current_files:
            # avoid overwriting files with same name
            file = f"{filename}-{cnt}.html"
            cnt = cnt + 1
        self.gcloud.upload_cloud_blob(src_path, file)
        url = base_url + self.gcloud.bucket_name + "/" + file
        return url

    def validate_filename(self, title):
        invalid_chars = ["/", "\\", ".", "<", ">", "|", "?", "*"]
        for ch in invalid_chars:
            if ch in title:
                msg = (
                    f'\nCannot save "{title}" as a filename.\nInvalid character: "{ch}"'
                )
                logging.error(msg)
                sys.exit()

    def update_style(self):
        style = self.html.head.style
        new_style = style.string
        substitutions = [
            ("font-size", "font_size"),
            ("background-color", "page_background_color"),
            ("background-color", "container_background_color"),
            ("max-height", "cover_img_max_height"),
            ("max-width", "cover_img_max_width"),
            ("height", "suppl_img_height"),
            ("width", "suppl_img_width"),
            ("height", "logo_height"),
            ("width", "logo_width"),
        ]
        for html_attr, var_name in substitutions:
            val = CFG["asg"]["slide_generator"]["html"][var_name]
            pattern = rf"{html_attr}:\s*{var_name}"
            replacement = rf"{html_attr}: {val}"
            new_style = re.sub(pattern, replacement, str(new_style))
            style.string = new_style

    def add_images(self, book_container, item):
        max_imgs_per_col = CFG["asg"]["slide_generator"]["html"][
            "max_images_per_column"
        ]
        max_suppl_imgs = CFG["asg"]["slide_generator"]["html"][
            "max_suppl_images_per_title"
        ]
        if len(item.image_urls) > 0:
            cover_img_data = {
                "class": "cover_image",
                "src": item.image_urls[0],
                "loading": "lazy",
                "alt": "missing image",
            }
            cover_img_tag = self.tag("img", None, cover_img_data)
            book_container.append(cover_img_tag)
            images_grid = self.tag("div", None, {"class": "suppl_images"})
            img_cnt = 0
            col_img_cnt = 0
            for img_url in item.image_urls[1:]:  # suppl images
                if img_cnt >= max_suppl_imgs:
                    break
                if col_img_cnt >= max_imgs_per_col:
                    book_container.append(images_grid)
                    images_grid = self.tag("div", None, {"class": "suppl_images"})
                    col_img_cnt = 0
                suppl_img_tag = self.tag(
                    "img",
                    None,
                    {"src": img_url, "loading": "lazy", "class": "suppl_image"},
                )
                images_grid.append(suppl_img_tag)
                col_img_cnt = col_img_cnt + 1
                img_cnt = img_cnt + 1
            book_container.append(images_grid)
        return book_container

    def get_text_tag(self, key, val, item):
        val = self.get_slide_text_key_map(key, val, item)
        if key in CFG["asg"]["slide_generator"]["html"]["bold_text"]:
            try:
                field, bolded_text = re.split(":", val, maxsplit=1)
                bold_tag = self.tag("b", bolded_text, None)
                text_tag = self.tag("p", f"{field}:", None)
                text_tag.append(bold_tag)
            except ValueError:
                text_tag = self.tag("b", val, None)
        else:
            text_tag = self.tag("p", val, None)
        return text_tag

    def tag(self, tag_type, tag_text, data):
        tag = self.html.new_tag(tag_type)
        if tag_text:
            tag.string = tag_text
        if data:
            for key, val in data.items():
                tag.attrs[key] = val
        return tag


class GoogleSlideGenerator(SlideGenerator):
    # constants
    EMU_INCH = 914400

    # methods
    def __init__(self, slides, gcloud, vendor):
        self.slides = slides
        self.gcloud = gcloud
        self.vendor = vendor
        self.slides_api_call_count = 0

    ###########################################################################
    def color_to_rgbcolor(self, color):
        red, green, blue = ImageColor.getrgb(color)
        return {"red": red / 255.0, "green": green / 255.0, "blue": blue / 255.0}

    def get_req_update_artemis_slide(
        self, deck_id, book_slide_id, item, text_bucket_path, g_reqs
    ):
        namespace = (
            f"{type(self).__name__}.{self.get_req_update_artemis_slide.__name__}"
        )

        bg_color = CFG["asg"]["slide_generator"]["bg_color"]
        slide_w = CFG["asg"]["slide_generator"]["slide_w"]
        slide_h = CFG["asg"]["slide_generator"]["slide_h"]
        gutter = CFG["asg"]["slide_generator"]["gutter"]
        addl_img_w = CFG["asg"]["slide_generator"]["addl_img_w"]
        addl_img_h = CFG["asg"]["slide_generator"]["addl_img_h"]
        image_count = len(item.image_urls)
        main_dim = self.get_main_image_size(image_count)

        logging.info(f"{namespace}: background to {bg_color}")
        g_reqs += self.get_req_slide_bg_color(
            book_slide_id, self.color_to_rgbcolor(bg_color)
        )

        logging.info(f"{namespace}: cover image on book slide")
        cover_url = item.image_urls.pop()
        g_reqs += self.get_req_create_image(
            book_slide_id,
            cover_url,
            main_dim,
            (gutter, gutter),
        )

        for i, url in enumerate(item.image_urls):
            if i > CFG["asg"]["slide_generator"]["text_box_resize_img_threshold"]:
                continue

            logging.info(f"{namespace}: {i + 2!s} image on book slide")
            g_reqs += self.get_req_create_image(
                book_slide_id,
                url,
                (addl_img_w, addl_img_h),
                (
                    (gutter + ((addl_img_w + gutter) * i)),
                    (slide_h - gutter - addl_img_h),
                ),
            )

        logging.info(f"{namespace}: Create text")
        text_box_dim, max_lines = self.get_text_box_size_lines(image_count)
        big_text = self.create_slide_text(item, max_lines)

        logging.info(f"{namespace}: Create text image")
        text_filepath = self.create_text_image_file(
            item.isbn, text_bucket_path, big_text, text_box_dim
        )

        logging.info(f"{namespace}: Upload text image to GC storage")
        cdr, car_file = os.path.split(text_filepath)
        cdr, car_prefix = os.path.split(cdr)
        blob_name = car_prefix + "/" + car_file
        self.gcloud.upload_cloud_blob(text_filepath, blob_name)
        logging.debug(f"{namespace}: Deleting local text image")
        os.remove(text_filepath)
        logging.info(f"{namespace}: Create URL for text image")
        url = self.gcloud.generate_cloud_signed_url(blob_name)
        logging.info(f"{namespace}: text image to slide")
        g_reqs += self.get_req_create_image(
            book_slide_id, url, text_box_dim, (slide_w / 2, gutter)
        )

        logging.info(f"{namespace}: ISBN text on book slide")
        text_box_w = slide_w
        text_box_h = gutter
        text_fields = self.create_text_fields_via_batch_update(
            deck_id,
            self.get_req_create_text_box(
                book_slide_id,
                (
                    slide_w - CFG["asg"]["slide_generator"]["tiny_isbn_x_inset"],
                    slide_h - gutter,
                ),
                (text_box_w, text_box_h),
            ),
        )
        text_field_id = text_fields[0]
        text_d = {text_field_id: item.isbn}
        g_reqs += self.get_req_insert_text(text_d)
        g_reqs += self.get_req_text_field_fontsize(
            text_field_id, CFG["asg"]["slide_generator"]["tiny_isbn_fontsize"]
        )
        g_reqs += self.get_req_text_field_color(
            text_field_id,
            self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["text_color"]),
        )

        logging.info(f"{namespace}: logo image on book slide")
        g_reqs += self.get_req_create_logo(book_slide_id)

        return g_reqs

    def create_text_fields_via_batch_update(self, deck_id, reqs):
        text_object_id_list = []
        rsp = self.slide_batch_update_get_replies(deck_id, reqs)
        for obj in rsp:
            text_object_id_list.append(obj["createShape"]["objectId"])
        return text_object_id_list

    def create_book_slides_via_batch_update(self, deck_id, book_list):
        namespace = (
            f"{type(self).__name__}.{self.create_book_slides_via_batch_update.__name__}"
        )

        logging.info(f"{namespace}: Create slides for books")
        book_slide_id_list = []
        reqs = []
        for _i in range(len(book_list)):
            reqs += [
                {"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}}
            ]
        rsp = self.slide_batch_update_get_replies(deck_id, reqs)
        for i in rsp:
            book_slide_id_list.append(i["createSlide"]["objectId"])
        return book_slide_id_list

    def slide_batch_update(self, deck_id, reqs):
        try:
            res = (
                self.slides.presentations()
                .batchUpdate(body={"requests": reqs}, presentationId=deck_id)
                .execute()
            )
        except Exception as e:
            logging.error(f"Failed to update slide batch: Errror: {e}")
            res = None

        return res

    def slide_batch_update_get_replies(self, deck_id, reqs):
        return (
            self.slides.presentations()
            .batchUpdate(body={"requests": reqs}, presentationId=deck_id)
            .execute()
            .get("replies")
        )

    def get_req_create_image(self, slide_id, url, size, translate):
        w, h = size
        translate_x, translate_y = translate
        reqs = [
            {
                "createImage": {
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {
                                "magnitude": self.EMU_INCH * w,
                                "unit": "EMU",
                            },
                            "height": {
                                "magnitude": self.EMU_INCH * h,
                                "unit": "EMU",
                            },
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self.EMU_INCH * translate_x,
                            "translateY": self.EMU_INCH * translate_y,
                            "unit": "EMU",
                        },
                    },
                    "url": url,
                },
            }
        ]
        return reqs

    def get_req_create_logo(self, slide_id):
        # Place logo in upper right corner of slide
        # TODO: (#163) move this to CFG
        translate_x = (
            CFG["asg"]["slide_generator"]["slide_w"]
            - CFG["asg"]["slide_generator"]["logo_w"]
        )
        translate_y = 0
        return self.get_req_create_image(
            slide_id,
            CFG["asg"]["slide_generator"]["logo_url"],
            (
                CFG["asg"]["slide_generator"]["logo_w"],
                CFG["asg"]["slide_generator"]["logo_h"],
            ),
            (translate_x, translate_y),
        )

    def get_req_slide_bg_color(self, slide_id, rgb_d):
        reqs = [
            {
                "updatePageProperties": {
                    "objectId": slide_id,
                    "fields": "pageBackgroundFill",
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "solidFill": {
                                "color": {
                                    "rgbColor": rgb_d,
                                }
                            }
                        }
                    },
                },
            },
        ]
        return reqs

    def get_req_text_field_color(self, field_id, rgb_d):
        reqs = [
            {
                "updateTextStyle": {
                    "objectId": field_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": rgb_d,
                            }
                        }
                    },
                    "fields": "foregroundColor",
                }
            }
        ]
        return reqs

    def get_req_text_field_fontsize(self, field_id, pt_size):
        reqs = [
            {
                "updateTextStyle": {
                    "objectId": field_id,
                    "textRange": {"type": "ALL"},
                    "style": {
                        "fontSize": {
                            "magnitude": pt_size,
                            "unit": "PT",
                        }
                    },
                    "fields": "fontSize",
                }
            },
        ]
        return reqs

    def get_req_insert_text(self, text_dict):
        reqs = []
        for key in text_dict:
            reqs.append(
                {
                    "insertText": {
                        "objectId": key,
                        "text": text_dict[key],
                    },
                }
            )
        return reqs

    def get_req_create_text_box(self, slide_id, coord=(0, 0), field_size=(1, 1)):
        reqs = [
            {
                "createShape": {
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "width": {
                                "magnitude": self.EMU_INCH * field_size[0],
                                "unit": "EMU",
                            },
                            "height": {
                                "magnitude": self.EMU_INCH * field_size[1],
                                "unit": "EMU",
                            },
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": self.EMU_INCH * coord[0],
                            "translateY": self.EMU_INCH * coord[1],
                            "unit": "EMU",
                        },
                    },
                    "shapeType": "TEXT_BOX",
                },
            }
        ]
        return reqs

    def create_slide_text(self, item, max_lines):
        namespace = f"{type(self).__name__}.{self.create_slide_text.__name__}"

        big_text = ""
        logging.debug(f"{namespace}: Item.data: {item.data}")
        for k in item.data:
            key = k.strip().upper()
            if key in CFG["asg"]["slide_generator"]["blacklist_keys"]:
                continue
            if isinstance(item.data[k], dict):
                for sub_k in item.data[k]:
                    key = sub_k.strip().upper()
                    if key in CFG["asg"]["slide_generator"]["blacklist_keys"]:
                        continue
                    t = self.get_slide_text_key_map(key, item.data[k][sub_k], item)
                    line_count = big_text.count("\n")
                    t = textwrap.fill(
                        t,
                        width=CFG["asg"]["slide_generator"]["text_width"],
                        max_lines=max_lines - line_count,
                    )
                    t = t + "\n\n"
                    big_text += t
            else:
                t = self.get_slide_text_key_map(key, item.data[k], item)
                line_count = big_text.count("\n")
                t = textwrap.fill(
                    t,
                    width=CFG["asg"]["slide_generator"]["text_width"],
                    max_lines=max_lines - line_count,
                )
                t = t + "\n\n"
                big_text += t
        return big_text

    def create_text_image_file(self, isbn, text_bucket_path, text, size):
        namespace = f"{type(self).__name__}.{self.create_text_image_file.__name__}"

        line_spacing = CFG["asg"]["slide_generator"]["line_spacing"]
        slide_ppi = CFG["asg"]["slide_generator"]["slide_ppi"]
        w, h = size
        image = Image.new(
            "RGB",
            (int(w * slide_ppi), int(h * slide_ppi)),
            ImageColor.getrgb(CFG["asg"]["slide_generator"]["bg_color"]),
        )

        fontsize = 1
        for typeface in (
            "arial.ttf",
            "LiberationSans-Regular.ttf",
            "DejaVuSans.ttf",
        ):
            try:
                font = ImageFont.truetype(typeface, fontsize)
                break
            except OSError:
                font = None
                continue
        if not font:
            logging.error(f"{namespace}: Cannot access typeface '{typeface}'")
            return None
        draw = ImageDraw.Draw(image)

        # dynamically size text to fit box
        while (
            draw.multiline_textbbox(
                xy=(0, 0), text=text, font=font, spacing=line_spacing
            )[2]
            < image.size[0]
            and draw.multiline_textbbox(
                xy=(0, 0), text=text, font=font, spacing=line_spacing
            )[3]
            < image.size[1]
            and fontsize < CFG["asg"]["slide_generator"]["max_fontsize"]
        ):
            fontsize += 1
            font = ImageFont.truetype(typeface, fontsize)

        fontsize -= 1
        logging.info(f"{namespace}: Font size is '{fontsize}'")
        font = ImageFont.truetype(typeface, fontsize)

        # center text
        _delme1, _delme2, t_w, t_h = draw.multiline_textbbox(
            xy=(0, 0), text=text, font=font, spacing=line_spacing
        )
        y_offset = math.floor((image.size[1] - t_h) / 2)

        draw.multiline_text(
            (0, y_offset), text, font=font, spacing=line_spacing
        )  # put the text on the image
        text_file = f"{isbn!s}_text.png"
        text_file = os.path.join(text_bucket_path, text_file)
        image.save(text_file)
        return text_file

    def set_image_blob_list(self, bucket_prefix):
        self.image_blob_list = self.gcloud.list_image_blob_names(bucket_prefix)

    def get_item_image_blob_list(self, item):
        # FIXME:  This should happen in Item object at time of instantiation.
        if not item.isbn and "TBCODE" in item.data:
            item.isbn = item.data["TBCODE"]
        image_list = [blob for blob in self.image_blob_list if str(item.isbn) in blob]
        return sorted(image_list)

    def get_cloud_urls(self, item):
        sl = self.get_item_image_blob_list(item)
        # generate URLs for item images on google cloud storage
        url_list = []
        for name in sl:
            url = self.gcloud.generate_cloud_signed_url(name)
            url_list.append(url)

        return url_list

    def get_text_bucket_prefix(self, bucket_prefix):
        # hack a text_bucket_prefix value
        text_bucket_prefix = bucket_prefix.replace("images", "text")
        if text_bucket_prefix == bucket_prefix:
            text_bucket_prefix = bucket_prefix + "_text"
        return text_bucket_prefix

    ####################################################################################
    def generate(self, items, bucket_prefix, deck_title=None):  # noqa: PLR0915
        namespace = f"{type(self).__name__}.{self.generate.__name__}"

        logging.info(f"{namespace}: Getting image blob list")
        self.set_image_blob_list(bucket_prefix)

        slide_max_batch = CFG["asg"]["slide_generator"]["slide_max_batch"]
        text_bucket_prefix = self.get_text_bucket_prefix(bucket_prefix)
        text_bucket_path = os.path.join(artemis_sg.data_dir, text_bucket_prefix)
        if not os.path.isdir(text_bucket_path):
            os.mkdir(text_bucket_path)

        logging.info(f"{namespace}: Deleting GCloud files in {text_bucket_prefix}")
        self.gcloud.delete_prefix_blobs(text_bucket_prefix)

        logging.info(f"{namespace}: Create new slide deck")
        utc_dt = datetime.datetime.now(datetime.timezone.utc)
        local_time = utc_dt.astimezone().isoformat()
        title = f"{self.vendor.name} Artemis Slides {local_time}"
        data = {"title": title}
        rsp = self.slides.presentations().create(body=data).execute()
        self.slides_api_call_count += 1
        deck_id = rsp["presentationId"]

        title_slide = rsp["slides"][0]
        title_slide_id = title_slide["objectId"]
        title_id = title_slide["pageElements"][0]["objectId"]
        subtitle_id = title_slide["pageElements"][1]["objectId"]

        reqs = []
        logging.info(f"{namespace}: req Insert slide deck title+subtitle")
        subtitle = self.vendor.name
        if deck_title:
            subtitle = f"{subtitle}, {deck_title}"
        title_card_text = {
            title_id: "Artemis Book Sales Presents...",
            subtitle_id: subtitle,
        }
        reqs += self.get_req_insert_text(title_card_text)
        reqs += self.get_req_text_field_fontsize(title_id, 40)
        reqs += self.get_req_text_field_color(
            title_id,
            self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["text_color"]),
        )
        reqs += self.get_req_text_field_color(
            subtitle_id,
            self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["text_color"]),
        )
        reqs += self.get_req_slide_bg_color(
            title_slide_id,
            self.color_to_rgbcolor(CFG["asg"]["slide_generator"]["bg_color"]),
        )
        reqs += self.get_req_create_logo(title_slide_id)

        # find images and delete books entries without images
        # using blob list as proxy for final urls to be generated later.
        for item in items:
            item.image_urls = self.get_item_image_blob_list(item)

        # update title slide
        self.slide_batch_update(deck_id, reqs)
        # clear reqs
        reqs = []
        # create book slides
        items_with_images = items.get_items_with_image_urls()
        book_slide_id_list = self.create_book_slides_via_batch_update(
            deck_id, items_with_images
        )

        e_books = list(zip(book_slide_id_list, items_with_images))
        batches = math.ceil(len(e_books) / slide_max_batch)
        upper_index = len(e_books)
        offset = 0
        for _b in range(batches):
            upper = offset + slide_max_batch
            upper = min(upper, upper_index)
            for book_slide_id, book in e_books[offset:upper]:
                book.image_urls = self.get_cloud_urls(book)
                reqs = self.get_req_update_artemis_slide(
                    deck_id, book_slide_id, book, text_bucket_path, reqs
                )
            logging.info(f"{namespace}: Execute img/text update reqs")
            # pp.pprint(reqs)
            # exit()
            self.slide_batch_update(deck_id, reqs)
            reqs = []
            offset = offset + slide_max_batch

        logging.info(f"{namespace}: Slide deck completed")
        logging.info(f"{namespace}: Deleting GCloud files in {text_bucket_prefix}")
        self.gcloud.delete_prefix_blobs(text_bucket_prefix)
        logging.info(f"{namespace}: API call counts")
        link = f"https://docs.google.com/presentation/d/{deck_id}"
        logging.info(f"{namespace}: Slide deck link: {link}")
        return link

    def get_main_image_size(self, image_count):
        w = (CFG["asg"]["slide_generator"]["slide_w"] / 2) - (
            CFG["asg"]["slide_generator"]["gutter"] * 2
        )
        h = CFG["asg"]["slide_generator"]["slide_h"] - (
            CFG["asg"]["slide_generator"]["gutter"] * 2
        )
        if image_count > 1:
            h = (
                CFG["asg"]["slide_generator"]["slide_h"]
                - (CFG["asg"]["slide_generator"]["gutter"] * 3)
                - (CFG["asg"]["slide_generator"]["addl_img_h"])
            )
        return (w, h)

    def get_text_box_size_lines(self, image_count):
        w = (CFG["asg"]["slide_generator"]["slide_w"] / 2) - (
            CFG["asg"]["slide_generator"]["gutter"] * 2
        )
        h = CFG["asg"]["slide_generator"]["slide_h"] - (
            CFG["asg"]["slide_generator"]["gutter"] * 2
        )
        max_lines = CFG["asg"]["slide_generator"]["text_box_max_lines"]
        if image_count > CFG["asg"]["slide_generator"]["text_box_resize_img_threshold"]:
            h = (
                CFG["asg"]["slide_generator"]["slide_h"]
                - (CFG["asg"]["slide_generator"]["gutter"] * 2)
                - (CFG["asg"]["slide_generator"]["addl_img_h"])
            )
            max_lines = CFG["asg"]["slide_generator"]["text_box_resized_max_lines"]
        return (w, h), max_lines

    ###########################################################################


def main(vendor_code, sheet_id, worksheet, scraped_items_db, title, flags):
    # namespace = "slide_generator.main"

    # vendor object
    html = flags.get("html")
    # mailchimp = flags.get("mailchimp")
    vendr = vendor(vendor_code)
    cloud_key_file = CFG["google"]["cloud"]["key_file"]
    creds = app_creds()
    sheet_data = spreadsheet.get_sheet_data(sheet_id, worksheet)
    sheet_keys = sheet_data.pop(0)
    items_obj = Items(sheet_keys, sheet_data, vendr.isbn_key)
    items_obj.load_scraped_data(scraped_items_db)
    if html:
        bucket_name = CFG["google"]["cloud"]["public_html_bucket"]
        gcloud = GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)
        template = importlib.resources.files(artemis_sg.data).joinpath("template.html")
        url = HtmlSlideGenerator(gcloud, vendr, template, title).generate(items_obj)
        url_type = "HTML Slide deck"
    else:
        bucket_name = CFG["google"]["cloud"]["bucket"]
        bucket_prefix = CFG["google"]["cloud"]["bucket_prefix"]
        gcloud = GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)
        # GCloud object
        slides = build("slides", "v1", credentials=creds)
        sg = GoogleSlideGenerator(slides, gcloud, vendr)
        url = sg.generate(items_obj, bucket_prefix, title)
        url_type = "Google Slide deck"
    deck_text = Text(f"{url_type}: {url}")
    deck_text.stylize("green")
    console.print(deck_text)
