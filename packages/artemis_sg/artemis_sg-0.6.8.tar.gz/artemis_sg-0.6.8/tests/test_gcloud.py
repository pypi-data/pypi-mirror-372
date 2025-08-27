# ruff: noqa: S101
import logging
import os
import time

import pytest

from artemis_sg.config import CFG
from artemis_sg.gcloud import GCloud
from artemis_sg.gcloud import main as gcloud_main


@pytest.fixture()
def valid_cloud():
    bucket_name = CFG["google"]["cloud"]["bucket"]
    cloud_key_file = CFG["google"]["cloud"]["key_file"]
    return GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)


@pytest.mark.integration()
def test_upload_cloud_blob(valid_cloud, source_file):
    """
    GIVEN a GCloud object with a valid bucket name
    AND a local file
    WHEN upload_cloud_blob method is called on the object
    THEN no exception is thrown
    """
    val = valid_cloud.upload_cloud_blob(source_file, "test_prefix/test_file.txt")

    assert val is None


@pytest.mark.integration()
def test_generate_cloud_signed_url(valid_cloud):
    """
    GIVEN a GCloud object with a valid bucket name
    WHEN generate_cloud_signed_urlupload_cloud_blob method is called on the object
    THEN a storage.googleapis.com url is returned
    """
    url = valid_cloud.generate_cloud_signed_url("test_prefix/test_file.txt")

    bucket_name = CFG["google"]["cloud"]["bucket"]
    expected_str = f"https://storage.googleapis.com/{bucket_name}/test_prefix/test_file.txt?X-Goog-Algorithm="
    assert isinstance(url, str)
    assert expected_str in url


@pytest.mark.integration()
def test_list_blobs(valid_cloud):
    """
    GIVEN a GCloud object with a valid bucket name
    AND an existing blob in the bucket with known prefix
    WHEN list_blobs method is called on the object with known prefix
    THEN a blob iterator object is returned
         containing a blob object with the expected name
    """
    blobs = valid_cloud.list_blobs("test_prefix")

    blob = next(blobs)

    # FIXME: should not depend on test_upload_cloud_blob
    assert blob.name == "test_prefix/test_file.txt"


@pytest.mark.integration()
def test_list_blobs_does_not_exist(valid_cloud):
    """
    GIVEN a GCloud object with a valid bucket name
    WHEN list_blobs method is called on the object with an invalid prefix
    THEN a blob object is returned with the expected name
    """
    blobs = valid_cloud.list_blobs("invalid_prefix")

    with pytest.raises(StopIteration):
        next(blobs)


@pytest.mark.integration()
def test_main_old_existing_files_not_upload(caplog, populated_target_directory):
    """
    GIVEN a local file directory
    AND it contains a file that exists as a blob in GCloud
    AND the file is old
    WHEN Gcloud.main is called
    THEN the file is not uploaded
    """
    caplog.set_level(logging.INFO)
    image_file = "9999999999990.jpg"
    image_directory = str(populated_target_directory)
    CFG["asg"]["data"]["dir"]["upload_source"] = image_directory
    filepath = os.path.join(image_directory, image_file)

    # make image_file old
    one_day = 1 * 60 * 60 * 24
    old_time = time.time() - one_day
    os.utime(filepath, (old_time, old_time))

    gcloud_main()

    assert (
        "root",
        logging.INFO,
        (
            f"gcloud.upload: File '{image_file}' "
            f"found in Google Cloud bucket, not uploading."
        ),
    ) in caplog.record_tuples


@pytest.mark.integration()
def test_main_new_existing_files_upload(caplog, populated_target_directory):
    """
    GIVEN a local file directory
    AND it contains a file that exists as a blob in GCloud
    AND the file is new
    WHEN Gcloud.main is called
    THEN the file is uploaded
    """
    caplog.set_level(logging.INFO)
    image_file = "9999999999990.jpg"
    image_directory = str(populated_target_directory)
    CFG["asg"]["data"]["dir"]["upload_source"] = image_directory
    blob_name = f"{CFG['google']['cloud']['bucket_prefix']}/{image_file}"

    gcloud_main()

    assert (
        "root",
        logging.INFO,
        f"gcloud.upload: Uploading '{blob_name}' to Google Cloud bucket.",
    ) in caplog.record_tuples


@pytest.mark.integration()
def test_main_non_image_files_not_uploaded_deleted(caplog, populated_target_directory):
    """
    GIVEN a local file directory
    AND it contains a file that is not an image
    WHEN Gcloud.main is called
    THEN the file is not uploaded
    AND the file is deleted
    """
    caplog.set_level(logging.INFO)
    image_file = "9999999999999.jpg"
    image_directory = str(populated_target_directory)
    filepath = os.path.join(image_directory, image_file)
    CFG["asg"]["data"]["dir"]["upload_source"] = image_directory

    gcloud_main()

    assert (
        "root",
        logging.ERROR,
        f"gcloud.upload: Err reading '{image_file}', deleting '{filepath}'",
    ) in caplog.record_tuples
    assert not os.path.exists(filepath)
