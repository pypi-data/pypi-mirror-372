# ruff: noqa: S101
import os
from unittest.mock import Mock

import pytest
from googleapiclient.discovery import build

from artemis_sg import slide_generator
from artemis_sg.app_creds import app_creds
from artemis_sg.config import CFG
from artemis_sg.gcloud import GCloud
from artemis_sg.items import Items
from artemis_sg.vendor import vendor


def test_generate(items_collection):
    """
    Given a SlideGenerator object
    When the generate() method is called on it
    Then it returns a slide deck link with the expected ID
    """
    slides_dict = {
        "objectId": "fooSlide",
        "pageElements": [
            {"objectId": "fooElem0"},
            {"objectId": "fooElem1"},
        ],
    }
    gcloud = Mock()
    gcloud.list_image_blob_names.return_value = []
    vendor = Mock()
    slides = Mock()
    call_chain1 = "presentations.return_value.create.return_value.execute.return_value"
    call_chain2 = (
        "presentations.return_value."
        "batchUpdate.return_value."
        "execute.return_value."
        "get.return_value"
    )
    config = {
        "name": "mocky_slides",
        call_chain1: {"presentationId": "MyPresId", "slides": [slides_dict]},
        call_chain2: [{"createSlide": {"objectId": "MySlideId"}}],
    }
    slides.configure_mock(**config)

    sg_obj = slide_generator.GoogleSlideGenerator(slides, gcloud, vendor)
    link = sg_obj.generate(items_collection, "bucket_pre", "Cool title")

    assert link == "https://docs.google.com/presentation/d/MyPresId"


def test_blacklisted_keys():
    """
    Given a SlideGenerator object
    When the create_slide_text() method is called on it
    Then the object's blacklisted keys do not appear in text
    """

    class MockItem:
        def __init__(self):
            self.data = {"AUTHOR": "Dr. Seuss"}
            self.isbn_key = "ISBN"
            for blacklisted in CFG["asg"]["slide_generator"]["blacklist_keys"]:
                self.data[blacklisted] = "I should not be here!"

    sg_obj = slide_generator.GoogleSlideGenerator("foo", "bar", "baz")
    text = sg_obj.create_slide_text(MockItem(), 99)

    assert "Seuss" in text
    for blacklisted in CFG["asg"]["slide_generator"]["blacklist_keys"]:
        assert blacklisted not in text


def test_gj_binding_map():
    """
    Given a SlideGenerator object
    When the gj_binding_map() method is called on it
    Then the expected value is returned
    """
    m = {
        "P": "Paperback",
        "H": "Hardcover",
        "C": "Hardcover",
        "C NDJ": "Cloth, no dust jacket",
        "CD": "CD",
    }
    sg_obj = slide_generator.SlideGenerator()

    for key, value in m.items():
        assert sg_obj.gj_binding_map(key) == value


def test_gj_type_map():
    """
    Given a SlideGenerator object
    When the gj_type_map() method is called on it
    Then the expected value is returned
    """
    m = {
        "R": "Remainder",
        "h": "Return",
    }
    sg_obj = slide_generator.SlideGenerator()

    for key, value in m.items():
        assert sg_obj.gj_type_map(key) == value


def test_get_req_update_artemis_slide(monkeypatch, items_collection, target_directory):
    """
    Given a SlideGenerator object
    When the get_req_update_artemis_slide() method is called on it
    AND global requests is returned
    AND it contains 'createImage' for the `item.image_urls`
    AND it contains 'insertText' for the text objectid
    AND gcloud.upload_cloud_blob is called with text image filepath
    AND gcloud.generate_cloud_signed_url is called
    """
    base_dict = {"placeholder": "here"}
    gcloud = Mock()
    slides = Mock()
    call_chain = (
        "presentations.return_value."
        "batchUpdate.return_value."
        "execute.return_value."
        "get.return_value"
    )
    config = {
        "name": "mocky_slides",
        call_chain: [{"createShape": {"objectId": "foobarbaz"}}],
    }
    slides.configure_mock(**config)
    item = items_collection.get_items()[0]
    item.image_urls = ["foo"]

    sg_obj = slide_generator.GoogleSlideGenerator(slides, gcloud, "vendor")
    g_reqs = sg_obj.get_req_update_artemis_slide(
        "deckid", "slideid", item, target_directory, [base_dict]
    )

    assert any(
        d.get("url") == "foo" for d in [d.get("createImage", base_dict) for d in g_reqs]
    )
    assert any(
        d.get("objectId") == "foobarbaz"
        for d in [d.get("insertText", base_dict) for d in g_reqs]
    )
    gcloud.upload_cloud_blob.assert_called  # noqa: B018
    gcloud.generate_cloud_signed_url.assert_called  # noqa: B018


@pytest.mark.database()
@pytest.mark.integration()
def test_slide_generator():
    """
    GIVEN a vendor object  # for vendor specific slide logic
    AND a Google Sheet ID
    AND a Google Sheet tab
    AND a Slides API object
    AND a GCloud API object
    AND a Items dataset unified from sheet and scraped data
    AND a SlideGenerator object given vendor, GCloud, and Slides objects
    WHEN we call the generate() method given Items, and title
    THEN a Google slide deck is created with given title and data
    """
    # vendor object
    vendr = vendor("sample")

    # sheet id
    sheet_id = CFG["asg"]["test"]["sheet"]["id"]
    sheet_tab = CFG["asg"]["test"]["sheet"]["tab"]

    creds = app_creds()
    slides = build("slides", "v1", credentials=creds)

    # GCloud object
    bucket_name = CFG["google"]["cloud"]["bucket"]
    cloud_key_file = CFG["google"]["cloud"]["key_file"]
    gcloud = GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)

    # Items dataset
    sheets = build("sheets", "v4", credentials=creds)
    sheet_data = (
        sheets.spreadsheets()
        .values()
        .get(range=sheet_tab, spreadsheetId=sheet_id)
        .execute()
        .get("values")
    )
    sheet_keys = sheet_data.pop(0)
    items_obj = Items(sheet_keys, sheet_data, vendr.isbn_key)
    items_obj.load_scraped_data("scraped_items.json")

    sg = slide_generator.GoogleSlideGenerator(slides, gcloud, vendr)

    bucket_prefix = CFG["google"]["cloud"]["bucket_prefix"]
    slide_deck = sg.generate(items_obj, bucket_prefix, "Cool title")

    assert slide_deck


def test_html_slide_generator(
    monkeypatch,
    items_collection,
    html_template_filepath,
    html_output,
    target_directory,
):
    """
    GIVEN an items collection
    AND a template html file
    AND a GCloud object
    AND a HtmlSlideGenerator object
    WHEN we call the generate method
    THEN a html file is created and uploaded to google cloud
    """
    foobar = Mock()
    gcloud = Mock()
    vendr = Mock()
    title = "foobar"
    monkeypatch.chdir(target_directory)
    monkeypatch.setattr(slide_generator.HtmlSlideGenerator, "upload", foobar)
    monkeypatch.setattr(slide_generator.HtmlSlideGenerator, "add_images", foobar)
    monkeypatch.setattr(slide_generator.HtmlSlideGenerator, "update_style", foobar)
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    sg.add_images.return_value = sg.tag("<div>", None, None)

    sg.generate(items_collection)
    sg.update_style.assert_called()
    sg.upload.assert_called()
    sg.add_images.assert_called()
    assert CFG["asg"]["slide_generator"]["logo_url"] in sg.html


def test_html_slide_generator_upload(html_output, html_template_filepath):
    """
    GIVEN a file source path
    AND a GCloud object
    AND a HtmlSlideGenerator object
    WHEN we call the upload method with the source path
    THEN a file is uploaded to google cloud
    """
    gcloud = Mock()
    vendr = Mock()
    gcloud.list_blobs.return_value = iter([])
    gcloud.bucket_name = "test_bucket_name"
    src_path, title = html_output
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    url = sg.upload(src_path)
    sg.gcloud.list_blobs.assert_called()
    sg.gcloud.upload_cloud_blob.assert_called()
    assert gcloud.bucket_name in url


def test_html_slide_generator_add_images(html_template_filepath, items_collection):
    """
    GIVEN a HtmlSlideGenerator object
    AND a gcloud object
    AND a template html file
    AND a html div tag
    AND a specified maximum number of images per title
    WHEN the add_images method is called
    THEN the correct images are added to the div tag
    """
    gcloud = Mock()
    vendr = Mock()
    title = "foobar"
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    book_container = sg.tag("div", None, None)
    item_w_images = items_collection.get_items()[0]
    item_w_images.image_urls = []
    max_suppl_images = CFG["asg"]["slide_generator"]["html"][
        "max_suppl_images_per_title"
    ]
    for cnt in range(max_suppl_images + 2):
        item_w_images.image_urls.append(f"img-{cnt}")
    new_book_container = sg.add_images(book_container, item_w_images)
    assert "suppl_images" in str(new_book_container)
    for cnt, img in enumerate(item_w_images.image_urls):
        if cnt > max_suppl_images:
            assert img not in str(new_book_container)
        else:
            assert img in str(new_book_container)


def test_html_slide_generator_add_images_for_items_without_images(
    html_template_filepath, items_collection
):
    """
    GIVEN a HtmlSlideGenerator object
    AND an html tag
    AND an item
    WHEN the add_images method is called
    THEN no images are added to the html tag
    """
    gcloud = Mock()
    vendr = Mock()
    title = "foobar"
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    item = items_collection.get_items()[0]
    item.image_urls = []
    book_container = sg.tag("div", None, None)
    new_book_container = sg.add_images(book_container, item)
    assert "suppl_images" not in str(new_book_container)


def test_html_slide_generator_tag(html_template_filepath):
    """
    GIVEN a HtmlSlideGenerator object
    AND a html tag type
    AND a dict of data containing attributes for a html tag
    WHEN the tag method is called
    THEN an appropriate html tag is returned.
    """
    gcloud = Mock()
    vendr = Mock()
    title = "foobar"
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )

    test_tag = sg.tag("p", "foo", {"class": "bar"})
    test_tag2 = sg.tag(
        "div", None, {"src": "img.png", "loading": "lazy", "alt": "missing_img"}
    )
    test_tag3 = sg.tag("title", "foobar", None)
    assert str(test_tag) == '<p class="bar">foo</p>'
    assert (
        str(test_tag2) == '<div alt="missing_img" loading="lazy" src="img.png"></div>'
    )
    assert str(test_tag3) == "<title>foobar</title>"


def test_html_slide_generator_update_style(html_template_filepath, html_output):
    """
    GIVEN a HtmlSlideGenerator object
    AND an html template file containing config variable names
    WHEN the update_style method is called
    THEN then the variable names are replaced with values in HtmlSlideGenerator.html

    """
    gcloud = Mock()
    vendr = Mock()
    path, title = html_output
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    sg.update_style()
    # each config variable in html should be replaced
    for key in CFG["asg"]["slide_generator"]["html"]:
        if key in ("max_images_per_column", "bold_text", "max_suppl_images_per_title"):
            continue
        assert key not in sg.html.style.string
        assert str(CFG["asg"]["slide_generator"]["html"][key]) in sg.html.style.string


def test_items_in_html(
    monkeypatch, html_template_filepath, html_output, target_directory, items_collection
):
    """
    GIVEN an items collection
    AND a template html file
    AND a HtmlSlideGenerator object
    WHEN we call the generate method
    THEN the html file being uploaded contains contents from the items collection
    """
    foobar = Mock()
    gcloud = Mock()
    vendr = Mock()
    monkeypatch.chdir(target_directory)
    monkeypatch.setattr(slide_generator.HtmlSlideGenerator, "upload", foobar)
    monkeypatch.setattr(os, "remove", foobar)
    path, title = html_output
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    bold_text_fields = CFG["asg"]["slide_generator"]["html"]["bold_text"]
    item_with_bolded_field = items_collection.get_items()[0]
    item_with_bolded_field.data[bold_text_fields[0]] = "foobar"
    sg.generate(items_collection)
    assert os.path.exists(path)
    with open(path) as file:
        file_content = file.read()
    assert "<b>\n    foobar\n   </b>" in file_content
    for item in items_collection.get_items():
        assert item.isbn in file_content


def test_slide_generator_get_slide_text_key_map(items_collection):
    """
    GIVEN an items_collection
    AND a SlideGenerator object
    WHEN get_slide_text_key_map is called
    THEN it returns the text map and no errors raised
    """
    sg = slide_generator.SlideGenerator()
    for item in items_collection.get_items():
        for key in item.data:
            if isinstance(item.data[key], dict):
                for subkey in item.data[key]:
                    res = sg.get_slide_text_key_map(key, item.data[key][subkey], item)
            else:
                res = sg.get_slide_text_key_map(key, item.data[key], item)
                if key == "ISBN":
                    assert res == f"ISBN: {item.isbn}"


def test_slide_generator_get_vendor_specific_slide_text_key_map(items_collection):
    """
    GIVEN an items collection
    AND a SlideGenerator object
    AND a text map defined in CFG["asg"]["slide_generator"]["text_map"][vendr.code][key]
    WHEN we call the get_vendor_specific_slide_text_key_map function
    THEN it returns the proper fstring.
    """
    vendr = vendor("sample")
    sg_obj = slide_generator.SlideGenerator()
    for item in items_collection.get_items():
        res = sg_obj.get_vendor_specific_slide_text_key_map("ISBN", item, vendr)
        assert res == f"www.sample_vendor_specific_text_map/{item.isbn}"


def test_htmlslidegenerator_get_text_tag(
    monkeypatch, html_template_filepath, html_output, target_directory, items_collection
):
    """
    GIVEN a HTMLSlideGenerator object and an Item
    AND gcloud object, vendor, and html template
    WHEN get_text_tag is called
    THEN the item data is returned as html
    """
    foobar = Mock()
    gcloud = Mock()
    monkeypatch.chdir(target_directory)
    monkeypatch.setattr(slide_generator.HtmlSlideGenerator, "upload", foobar)
    monkeypatch.setattr(os, "remove", foobar)
    path, title = html_output
    vendr = vendor("sample")
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    item = items_collection.get_items()[0]
    nested_key = "NESTED_KEY"
    nested_val = "bar"
    item.data["KEY1"] = {nested_key: nested_val}
    text_tag1 = sg.get_text_tag(nested_key, nested_val, item)
    text_tag2 = sg.get_text_tag("foo", "123", item)
    assert "<p>Nested_Key: bar</p>" in str(text_tag1)
    assert "Foo: 123" in str(text_tag2)


def test_html_slides_add_vendor_text_map_to_slides(
    monkeypatch, html_template_filepath, html_output, target_directory, items_collection
):
    """
    GIVEN an items collection
    AND a HtmlSlideGenerator object
    AND a vendor with a vendor code,
    AND a text map defined in CFG[asg][slide_generator][text_map][vendr code][key]
    WHEN we call the generate function
    THEN the text mapped fstrings are added to the html page.
    """
    foobar = Mock()
    gcloud = Mock()
    monkeypatch.chdir(target_directory)
    monkeypatch.setattr(slide_generator.HtmlSlideGenerator, "upload", foobar)
    monkeypatch.setattr(os, "remove", foobar)
    path, title = html_output
    vendr = vendor("sample")
    sg = slide_generator.HtmlSlideGenerator(
        gcloud, vendr, html_template_filepath, title
    )
    sg.generate(items_collection)
    assert os.path.exists(path)
    with open(path) as file:
        file_content = file.read()
    for item in items_collection.get_items():
        assert f"www.sample_vendor_specific_text_map/{item.isbn}" in file_content
    assert '<div class="page_number">' in file_content
