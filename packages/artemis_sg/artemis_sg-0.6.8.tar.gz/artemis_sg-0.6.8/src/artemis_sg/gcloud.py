#!/usr/bin/env python
"""artemis_sg.gcloud

Interface for Google Cloud blobs."""

import datetime
import logging
import os
import time
import typing as t

from google.cloud import storage

from artemis_sg.config import CFG
from artemis_sg.img_downloader import ImgDownloader

MODULE = os.path.splitext(os.path.basename(__file__))[0]


class GCloud:
    """
    Object that provides Google Cloud Bucket interaction.

    :param cloud_key_file:
        Path of file containing the authentication key for a Google Cloud.
    :param bucket_name:
        Name of the Google Cloud Bucket to be used by object instance.
    """

    def __init__(self, cloud_key_file: str, bucket_name: str = "default") -> None:
        # This environ setting needs to stay.
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cloud_key_file
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(self.bucket_name)

    def upload_cloud_blob(
        self, source_file_path: str, destination_blob_name: str
    ) -> None:
        """
        Upload local file to Google Cloud Bucket.

        :param source_file_path:
            Path of file to be uploaded to Google Cloud Bucket.
        :param destination_blob_name:
            Name of Google Cloud Bucket blob to be saved.
        """

        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)

    def generate_cloud_signed_url(self, blob_name: str) -> str:
        """Generates a v4 signed URL for downloading a blob.

        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.

        :param blob_name:
            Name of Google Cloud Bucket blob to obtain URL for.
        :returns: URL of blob
        """

        blob = self.bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=30),
            method="GET",
        )

        return url

    def list_blobs(self, prefix: str) -> t.Iterator[storage.Blob]:
        """
        Get Iterator of blobs filtered by prefix.

        :param prefix:
            Name of Google Cloud Bucket prefix used to filter blobs
        :returns: Iterator of matching Blob objects
        """

        # FIXME: use page_token
        # page_token = None
        blobs = self.storage_client.list_blobs(self.bucket_name, prefix=prefix)
        return blobs

    def list_image_blob_names(self, prefix: str) -> list[str]:
        """
        Get list of image blob names filtered by prefix.

        :param prefix:
            Name of Google Cloud Bucket prefix used to filter blobs
        :returns: List of matching Blob names
        """

        blobs = self.list_blobs(prefix)
        names = []
        for blob in blobs:
            if "image" in blob.content_type:
                names.append(blob.name)
        return names

    def delete_prefix_blobs(self, prefix: str) -> None:
        """
        Delete blobs from Google Cloud Bucket with given prefix.

        :param prefix:
            Name of Google Cloud Bucket prefix used determine storage location.
        """

        # Ensure that a prefix was provided
        # to prevent the deletion of the entire bucket.
        if prefix:
            blobs = self.list_blobs(prefix)
            while True:
                try:
                    blob = next(blobs)
                except StopIteration:
                    break

                if not blob:
                    break
                blob.delete()


def upload(file_source_dir: str, bucket_prefix: str, cloud_object: GCloud) -> None:
    """
    Upload files in source directory to Google Cloud Bucket.

    :param file_source_dir:
        Path to directory containing source files to upload.
    :param bucket_prefix:
        Name of Google Cloud Bucket prefix used determine storage location.
    :param cloud_object:
        Instance of artemis_sg.GCloud to handle API interactions.
    """

    max_filesize = 1048576  # 1 MB

    namespace = f"{MODULE}.{upload.__name__}"
    blob_names = cloud_object.list_image_blob_names(bucket_prefix)
    for filename in os.listdir(file_source_dir):
        filepath = os.path.join(file_source_dir, filename)
        if os.path.isfile(filepath):
            file_blob_name = f"{bucket_prefix}/{filename}"
            # verify the file is an image, otherwise delete it
            ext = ImgDownloader().get_image_ext(filepath)
            if not ext:
                logging.error(
                    f"{namespace}: Err reading '{filename}', deleting '{filepath}'"
                )
                os.remove(filepath)
                continue
            # validate file size
            file_size = os.path.getsize(filepath)
            if file_size > max_filesize:
                logging.warning(
                    f"{namespace}: File '{filename}' too large to upload. Skipping."
                )
                continue
            # don't upload existing blobs unless the file is new
            file_age = time.time() - os.path.getmtime(filepath)
            if (
                file_blob_name in blob_names
                and file_age > CFG["google"]["cloud"]["new_threshold_secs"]
            ):
                logging.info(
                    f"{namespace}: File '{filename}' found in Google Cloud "
                    f"bucket, not uploading."
                )
                continue
            else:
                logging.info(
                    f"{namespace}: Uploading '{file_blob_name}' to Google Cloud bucket."
                )
                cloud_object.upload_cloud_blob(filepath, file_blob_name)


def main() -> None:
    """
    Wrapper for uploading files to Google Cloud Bucket.
    """

    file_source_dir = CFG["asg"]["data"]["dir"]["upload_source"]
    bucket_name = CFG["google"]["cloud"]["bucket"]
    bucket_prefix = CFG["google"]["cloud"]["bucket_prefix"]
    cloud_key_file = CFG["google"]["cloud"]["key_file"]

    cloud_object = GCloud(cloud_key_file=cloud_key_file, bucket_name=bucket_name)
    upload(file_source_dir, bucket_prefix, cloud_object)


if __name__ == "__main__":
    main()
