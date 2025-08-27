import json
import os
import pathlib
import shutil
from inspect import getsourcefile

import pytest
from xprocess import ProcessStarter

from artemis_sg import items

THIS_DIR = os.path.dirname(getsourcefile(lambda: 0))
DATA_PATH = os.path.abspath(os.path.join(THIS_DIR, "data"))
SRC_PATH = os.path.abspath(os.path.join(THIS_DIR, "../src/artemis_sg"))


@pytest.fixture(scope="session")
def waveserver(xprocess):
    class Starter(ProcessStarter):
        timeout = 30
        terminate_on_interrupt = True
        # startup pattern
        pattern = "Server started"

        # command to start process
        args = (
            "python",
            os.path.abspath(os.path.join(DATA_PATH, "wave_site/wave_webserver.py")),
        )

    # ensure process is running and return its logfile
    logfile = xprocess.ensure("waveserver", Starter)  # noqa: F841

    conn = "http://localhost:22222"
    yield conn

    # clean up whole process tree afterwards
    xprocess.getinfo("waveserver").terminate()


@pytest.fixture()
def isbn13():
    return "9781680508604"


@pytest.fixture()
def spreadsheet_filepath():
    path = os.path.join(DATA_PATH, "test_sheet.xlsx")
    return path


@pytest.fixture()
def empty_filepath():
    path = os.path.join(DATA_PATH, "empty.jpg")
    return path


@pytest.fixture()
def jpg_filepath():
    path = os.path.join(DATA_PATH, "artemis_logo.jpg")
    return path


@pytest.fixture()
def png_filepath():
    path = os.path.join(DATA_PATH, "artemis_logo.png")
    return path


@pytest.fixture()
def image_filepath():
    path = os.path.join(DATA_PATH, "artemis_logo.png")
    return path


@pytest.fixture()
def target_directory(tmp_path_factory):
    path = tmp_path_factory.mktemp("data")
    yield path


@pytest.fixture()
def target_file(target_directory):
    def _myfile(target_directory, *fname):
        file_path = os.path.join(target_directory, *fname)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        pathlib.Path(file_path).touch()
        return file_path

    return _myfile


@pytest.fixture()
def populated_target_directory(tmp_path_factory, jpg_filepath, isbn13):
    path = tmp_path_factory.mktemp("data")
    shutil.copyfile(jpg_filepath, os.path.join(path, f"{isbn13}.jpg"))
    shutil.copyfile(jpg_filepath, os.path.join(path, f"{isbn13}-1.jpg"))
    shutil.copyfile(jpg_filepath, os.path.join(path, "9999999999990.jpg"))
    shutil.copyfile(jpg_filepath, os.path.join(path, "9999999999990-1.jpg"))
    with open(os.path.join(path, "9999999999999.jpg"), "w") as f:
        f.write("I am not an image file")
        f.close()
    yield path


@pytest.fixture()
def source_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    f = d / "test_file.txt"
    f.write_text("Hello, world!")
    return f


@pytest.fixture()
def sample_scraped_data():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    isbn10a = "0802157009"
    isbn10b = "069102555X"
    description_a = "Cool item Dude!"
    description_b = "Totally awesome item!"
    dimension_a = "42x42"
    dimension_b = "1x1"
    ranks = {"AMAZON": "#3", "AMAZON_UK": "#984"}
    image_urls = [
        "https://example.com/images/image_001.jpg",
        "https://example.com/images/image_002.jpg",
    ]

    sample_data = {
        isbn13a: {
            "isbn10": isbn10a,
            "DESCRIPTION": description_a,
            "DIMENSION": dimension_a,
            "RANKS": ranks,
            "image_urls": image_urls,
        },
        isbn13b: {
            "isbn10": isbn10b,
            "DESCRIPTION": description_b,
            "DIMENSION": dimension_b,
            "RANKS": ranks,
            "image_urls": image_urls,
        },
    }
    return sample_data


@pytest.fixture()
def expected_with_scraped_urls():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    isbn10a = "0802157009"
    isbn10b = "069102555X"
    description_a = "Cool item Dude!"
    description_b = "Totally awesome item!"
    dimension_a = "42x42"
    dimension_b = "1x1"
    image_urls = [
        "https://example.com/images/image_001.jpg",
        "https://example.com/images/image_002.jpg",
    ]
    ranks = {"AMAZON": "#3", "AMAZON_UK": "#984"}
    sample_data = {
        isbn13a: {
            "isbn10": isbn10a,
            "DESCRIPTION": description_a,
            "DIMENSION": dimension_a,
            "RANKS": ranks,
            "image_urls": image_urls,
        },
        isbn13b: {
            "isbn10": isbn10b,
            "DESCRIPTION": description_b,
            "DIMENSION": dimension_b,
            "RANKS": ranks,
            "image_urls": image_urls,
        },
    }
    return sample_data


@pytest.fixture()
def unique_scraped_element():
    data = {
        "9780802150493": {
            "isbn10": "0802150497",
            "DESCRIPTION": "Previously saved item.",
            "image_urls": [
                "https://m.media-amazon.com/images/I/411wjt6OyLL.jpg",
                "https://m.media-amazon.com/images/I/51A2KIR3RyL.jpg",
            ],
        }
    }
    return data


@pytest.fixture()
def valid_data(sample_scraped_data, unique_scraped_element):
    data = {}
    isbn13b = "9780691025551"
    # add second sample element and change description
    data[isbn13b] = sample_scraped_data[isbn13b]
    data[isbn13b]["DESCRIPTION"] = "Previously saved item."
    # add a unique one
    data.update(unique_scraped_element)
    return data


@pytest.fixture()
def valid_datafile(target_directory, valid_data):
    file_name = os.path.join(target_directory, "valid.json")

    json_string = json.dumps(valid_data)
    with open(file_name, "w") as filepointer:
        filepointer.write(json_string)
    yield file_name


@pytest.fixture()
def empty_datafile(target_directory):
    file_name = os.path.join(target_directory, "empty.json")
    with open(file_name, "a") as f:
        f.close()
    yield file_name


@pytest.fixture()
def sample_item_list():
    isbn13a = "9780802157003"
    isbn13b = "9780691025551"
    item_list = [
        ["ISBN", "Price", "Ranks"],
        [isbn13a, "$42", {"AMAZON": "123", "AMAZON_UK": "321"}],
        [isbn13b, "$69", {}],
    ]
    return item_list


@pytest.fixture()
def items_collection(sample_item_list):
    collection = items.Items(
        sample_item_list[0],
        sample_item_list[1:],
        "ISBN",
    )
    return collection


@pytest.fixture()
def html_template_filepath():
    path = os.path.join(SRC_PATH, "data/template.html")
    return path


@pytest.fixture()
def html_output(target_directory):
    path = os.path.join(target_directory, "out.html")
    title = "out"
    return path, title


@pytest.fixture()
def amazon_item_url():
    path = os.path.join(DATA_PATH, "amazon", "item_page.html")
    return pathlib.Path(path).as_uri()


@pytest.fixture()
def tb_item_url():
    path = os.path.join(DATA_PATH, "tb", "item_page.html")
    return pathlib.Path(path).as_uri()


@pytest.fixture()
def data_path():
    return DATA_PATH


@pytest.fixture()
def mock_requests_response():
    class MockResponse:
        pass

    mock_response = MockResponse()
    mock_response.text = "hello"

    return mock_response
