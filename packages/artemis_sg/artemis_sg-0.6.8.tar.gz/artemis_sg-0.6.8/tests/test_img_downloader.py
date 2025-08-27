# ruff: noqa: S101,PLR0913
import glob
import logging
import os
import shutil
import tempfile
from unittest.mock import Mock

import pytest

from artemis_sg import img_downloader
from artemis_sg.isbn import validate_isbn


def teardown_function():
    img_dloader_temp_dirs = glob.glob(
        os.path.join(tempfile.gettempdir(), "ImgDownloader-*")
    )
    for d in img_dloader_temp_dirs:
        shutil.rmtree(d)


@pytest.fixture()
def jpg_url_list():
    return ["https://example.org/foo.jpg", "https://example.org/bar.jpg"]


@pytest.fixture()
def png_url_list():
    return ["https://example.org/foo.png", "https://example.org/bar.png"]


@pytest.fixture()
def txt_url_list():
    return ["https://example.org/foo.txt", "https://example.org/bar.txt"]


@pytest.fixture()
def populated_target_directory(tmp_path_factory, isbn13, jpg_filepath):
    path = tmp_path_factory.mktemp("data")
    shutil.copyfile(jpg_filepath, os.path.join(path, f"{isbn13}.jpg"))
    shutil.copyfile(jpg_filepath, os.path.join(path, f"{isbn13}-1.jpg"))
    yield path


@pytest.fixture()
def mock_jpg_response(jpg_filepath):
    with open(jpg_filepath, mode="rb") as file:
        file_content = file.read()

    class MockResponse:
        pass

    mock_response = MockResponse()
    mock_response.content = file_content

    return mock_response


@pytest.fixture()
def mock_png_response(png_filepath):
    with open(png_filepath, mode="rb") as file:
        file_content = file.read()

    class MockResponse:
        pass

    mock_response = MockResponse()
    mock_response.content = file_content

    return mock_response


@pytest.fixture()
def mock_txt_response():
    class MockResponse:
        pass

    mock_response = MockResponse()
    mock_response.content = b"Hello, World!\n"

    return mock_response


@pytest.mark.parametrize(
    "key",
    ["9781680508604", "1680508601", "069102555X", "672125069899"],
    ids=["ISBN13", "ISBN10", "ISBN10(alpha)", "Invalid"],
)
def test_download(monkeypatch, key, mock_jpg_response, target_directory, jpg_url_list):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose key is {key}
    AND an existing target directory
    WHEN we run the download method with the dictionary and target directory
    THEN the image urls are downloaded to the target directory
    """
    # TODO: This code for validating the ISBN key is duplicated
    # from the body of the `download` method, but is needed in
    # this testing context to validate the expected file names.
    isbn = validate_isbn(key)
    if not isbn:
        isbn = key

    img_dict = {isbn: jpg_url_list}

    mock = Mock(return_value=mock_jpg_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dloader = img_downloader.ImgDownloader()
    dest = dloader.download(img_dict, str(target_directory))

    dest_files = os.listdir(dest)
    assert f"{isbn}.jpg" in dest_files
    assert f"{isbn}-1.jpg" in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_download_no_target_directory(
    monkeypatch, isbn13, mock_jpg_response, jpg_url_list
):
    """
    Given an ImgDownloader object
    AND a dictionary of images
    WHEN we run the download method without a target directory
    THEN the image urls are downloaded to a created target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = isbn13
    img_dict = {key: jpg_url_list}

    mock = Mock(return_value=mock_jpg_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dest = dloader.download(img_dict)

    dest_files = os.listdir(dest)
    assert f"{key}.jpg" in dest_files
    assert f"{key}-1.jpg" in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_download_idempotent(
    monkeypatch, isbn13, mock_jpg_response, populated_target_directory, jpg_url_list
):
    """
    Given an ImgDownloader object
    AND a dictionary of images
    AND an existing target directory
    AND an existing product image is in the target directory
    WHEN we run the download method with the dictionary and target directory
    THEN the image urls are not re-downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = isbn13
    img_dict = {key: jpg_url_list}

    mock = Mock(return_value=mock_jpg_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dest = dloader.download(img_dict, str(populated_target_directory))

    mock.assert_not_called()
    dest_files = os.listdir(dest)
    assert f"{key}.jpg" in dest_files
    assert f"{key}-1.jpg" in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_issue_231_download_invalid_url(
    monkeypatch, mock_jpg_response, target_directory, jpg_url_list
):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose first value contains an invalid URL
    AND whose second value contains a valid URL
    AND an existing target directory
    WHEN we run the download method with the dictionary and target directory
    THEN the method completes successfully
    AND the valid image url is downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = "672125069899"
    img_dict = {key: jpg_url_list}

    return_data = [
        ConnectionError,
        mock_jpg_response,
    ]
    mock_jpg = Mock(side_effect=return_data)
    monkeypatch.setattr(img_downloader.requests, "get", mock_jpg)

    dest = dloader.download(img_dict, str(target_directory))

    dest_files = os.listdir(dest)
    mock_jpg.assert_called_with(jpg_url_list[1], timeout=10)
    assert f"{key}.jpg" not in dest_files
    assert f"{key}-1.jpg" in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_download_png(
    monkeypatch, isbn13, mock_png_response, target_directory, png_url_list
):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose key is an isbn13
    AND contains URI for 'PNG' images
    AND an existing target directory
    WHEN we run the download method with the dictionary and target directory
    THEN the image urls are downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = isbn13
    img_dict = {key: png_url_list}

    mock = Mock(return_value=mock_png_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dest = dloader.download(img_dict, str(target_directory))

    dest_files = os.listdir(dest)
    assert f"{key}.png" in dest_files
    assert f"{key}-1.png" in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_download_url_already_present_and_not_image(
    monkeypatch, isbn13, mock_png_response, target_directory
):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose key is an isbn13
    AND an existing target directory
    AND a PNG file with the isbn13 name in the directory
    AND the PNG file is not a PNG file
    WHEN we run the download method with the dictionary and target directory
    THEN the image url is downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    dest = os.path.join(target_directory, f"{isbn13}.png")
    with open(dest, "w") as f:
        f.write("I am not an image file")
        f.close()

    mock = Mock(return_value=mock_png_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dloader._download_url("url", dest, isbn13)

    assert dloader.get_image_ext(os.path.join(dest)) == ".png"


def test_download_unsupported(
    caplog, monkeypatch, isbn13, mock_txt_response, target_directory, txt_url_list
):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose key is an isbn13
    AND contains URI for 'TXT' file
    AND an existing target directory
    WHEN we run the download method with the dictionary and target directory
    THEN the text urls are not downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = isbn13
    img_dict = {key: txt_url_list}

    mock = Mock(return_value=mock_txt_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dest = dloader.download(img_dict, str(target_directory))

    dest_files = os.listdir(dest)
    for url in img_dict[key]:
        assert (
            "root",
            logging.WARNING,
            (
                f"ImgDownloader._download_url: ISBN {key}, "
                f"Skipping unsupported file type in '{url}'"
            ),
        ) in caplog.record_tuples
    assert f"{key}.txt" not in dest_files
    assert f"{key}-1.txt" not in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_download_empty_in_cache(
    caplog,
    monkeypatch,
    isbn13,
    mock_jpg_response,
    target_directory,
    empty_filepath,
    jpg_url_list,
):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose key is an isbn13
    AND an existing target directory
    AND target directory has an empty file with the isbn13 name
    WHEN we run the download method with the dictionary and target directory
    THEN a warning is issued
    AND the image urls are downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = isbn13
    img_dict = {key: jpg_url_list}
    shutil.copyfile(empty_filepath, os.path.join(target_directory, f"{isbn13}.jpg"))

    mock = Mock(return_value=mock_jpg_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dest = dloader.download(img_dict, str(target_directory))

    dest_files = os.listdir(dest)
    for _url in img_dict[key]:
        assert (
            "root",
            logging.WARNING,
            "ImgDownloader.get_image_ext: non-image file found",
        ) in caplog.record_tuples
    assert f"{key}.txt" not in dest_files
    assert f"{key}-1.txt" not in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f))


def test_download_unsupported_in_cache(
    monkeypatch,
    isbn13,
    mock_jpg_response,
    target_directory,
    empty_filepath,
    jpg_url_list,
):
    """
    Given an ImgDownloader object
    AND a dictionary of images whose key is an isbn13
    AND an existing target directory
    AND target directory has a non-image file with the isbn13 name
    WHEN we run the download method with the dictionary and target directory
    THEN the image urls are downloaded to the target directory
    """
    dloader = img_downloader.ImgDownloader()
    key = isbn13
    img_dict = {key: jpg_url_list}
    with open(os.path.join(target_directory, f"{isbn13}.jpg"), mode="w") as f:
        f.write("Hello")
        f.close()

    mock = Mock(return_value=mock_jpg_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    dest = dloader.download(img_dict, str(target_directory))

    dest_files = os.listdir(dest)
    assert f"{key}.jpg" in dest_files
    assert f"{key}-1.jpg" in dest_files
    for f in dest_files:
        assert dloader.get_image_ext(os.path.join(dest, f)) == ".jpg"


def test_get_pem(monkeypatch, mock_requests_response, target_directory, target_file):
    """
    GIVEN a remote pem certificate (via mock_requests_response)
    WHEN get_pem is called on ImgDownloader instance
    THEN the certifi/cacert.pem ends in the remote certificate
    AND the remote certificate is returned
    """
    master_pem_path = target_file(target_directory, "certifi", "cacert.pem")
    mock = Mock(return_value=mock_requests_response)
    monkeypatch.setattr(img_downloader.requests, "get", mock)
    monkeypatch.setattr(
        img_downloader.sysconfig,
        "get_paths",
        lambda *args: {"purelib": target_directory},
    )

    dloader = img_downloader.ImgDownloader()
    response = dloader.get_pem()

    with open(master_pem_path) as f:
        lines = f.readlines()
    assert lines
    assert lines[-1] == mock_requests_response.text
    assert response == mock_requests_response.text


def test_download_url_raises_err_when_no_pem(
    monkeypatch, mock_requests_response, target_directory, target_file
):
    """
    GIVEN a URL that returns an SSLError
    WHEN _download_url is called
    THEN we tried to get pem
    AND an error is raised
    """
    mock = Mock(side_effect=img_downloader.requests.exceptions.SSLError("Testing"))
    monkeypatch.setattr(img_downloader.requests, "get", mock)

    with pytest.raises(img_downloader.requests.exceptions.SSLError):
        dloader = img_downloader.ImgDownloader()
        dloader._download_url("url", "image_path", "isbn")
        assert dloader.tried_get_pem


def test_main(monkeypatch):
    console = Mock()
    text = Mock()
    text_obj = Mock()
    text.return_value = text_obj
    monkeypatch.setattr(img_downloader, "console", console)
    monkeypatch.setattr(img_downloader, "Text", text)
    monkeypatch.setattr(
        img_downloader,
        "CFG",
        {"asg": {"data": {"file": {"scraped": "foo"}, "dir": {"images": "bar"}}}},
    )

    img_downloader.main()

    console.print.assert_called_with(text_obj)
