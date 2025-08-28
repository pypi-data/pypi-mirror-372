import logging
from typing import Tuple

import boto3

from .util import timeit

log = logging.getLogger("s3")


def bucket_key_from_uri(s3_uri: str) -> Tuple[str, str]:
    """
    Extract the bucket name and key from an S3 URI.

    Parameters
    ----------
    s3_uri : str
        The S3 URI (with or without s3://)

    Outputs
    -------
    bucket : str
        The bucket name
    key : str
        The key
    """

    # Remove the 's3://' prefix if it exists, and split the path into the bucket name and the key
    s3_uri = s3_uri.replace("s3://", "")
    bucket, key = s3_uri.split("/", 1)

    return bucket, key


@timeit
def read_file(s3_uri: str, encoding: str = "utf-8") -> str:
    """
    Read content from a file in an S3 bucket.

    Parameters
    ----------
    s3_uri : str
        The full S3 path to the file (s3://bucket-name/path/to/file).
    encoding : str, default='utf-8'
        The character encoding to use when decoding the file content. If None, the file is read as binary.

    Outputs
    -------
    content : str or bytes
        The content of the file.
    """
    log.info(f"Reading file from {s3_uri}")
    # Remove the 's3://' prefix and split the path into the bucket name and the key
    bucket, key = bucket_key_from_uri(s3_uri)

    # Create an S3 session
    s3 = boto3.resource("s3")

    # Download the file from the S3 bucket
    obj = s3.Object(bucket, key)
    content = obj.get()["Body"].read()

    if encoding:
        content = content.decode(encoding)

    return content


@timeit
def upload_file(file_path: str, s3_uri: str):
    """
    Upload a file to an S3 bucket.

    Parameters
    ----------
    file_path : str
        The local path to the file to upload.
    s3_uri : str
        The full S3 URI (s3://bucket-name/path/to/file).

    Notes
    -----
    This function reads the file in binary mode and uploads it to the specified S3 location.

    Examples
    --------
    Upload a PDF file:
    >>> upload_file_to_s3("path/to/your/file.pdf", "s3://your-bucket-name/path/to/file.pdf")
    """
    log.info(f"Uploading file to {s3_uri}")
    bucket, key = bucket_key_from_uri(s3_uri)
    s3 = boto3.resource("s3")

    try:
        with open(file_path, "rb") as file:
            s3.Object(bucket, key).put(Body=file)
        log.info(f"Successfully uploaded file to {s3_uri}")
    except boto3.exceptions.S3UploadFailedError as e:
        log.error(f"Failed to upload file to {s3_uri}: {e}")
        raise


@timeit
def upload_content(content: str, s3_uri: str, encoding: str = "utf-8"):
    """
    Upload content to an S3 bucket.

    Parameters
    ----------
    content : str
        The content to write to the file.
    s3_uri : str
        The full S3 URI (s3://bucket-name/path/to/file).
    encoding : str, default='utf-8'
        The character encoding to use when encoding the text. If None, the content is treated as binary.

    Examples
    --------
    Upload a JSON string:
    >>> json_content = {"metadataAttributes": {"rel_path": "this-is-a-test", "year": 2016, "publisher": "ISO"}}
    >>> json_string = json.dumps(json_content)
    >>> upload_content_to_s3(json_string, "s3://your-bucket-name/path/to/aviation.metadata.json")

    Upload plain text:
    >>> text_content = "This is a plain text content."
    >>> upload_content_to_s3(text_content, "s3://your-bucket-name/path/to/textfile.txt")

    Upload a pickled object:
    >>> import pickle
    >>> obj = {"key": "value"}
    >>> pickled_obj = pickle.dumps(obj)
    >>> upload_content_to_s3(pickled_obj, "s3://your-bucket-name/path/to/object.pkl", encoding=None)
    """
    log.info(f"Uploading content to {s3_uri}")
    bucket, key = bucket_key_from_uri(s3_uri)
    s3 = boto3.resource("s3")

    try:
        if encoding:
            s3.Object(bucket, key).put(Body=content.encode(encoding))
        else:
            s3.Object(bucket, key).put(Body=content)
        log.info(f"Successfully uploaded content to {s3_uri}")
    except boto3.exceptions.S3UploadFailedError as e:
        log.error(f"Failed to upload content to {s3_uri}: {e}")
        raise


def s3_exists(s3_uri: str) -> bool:
    """
    Check if a file exists at an s3 URI

    Parameters
    ----------
    s3_uri : str
        The full S3 path to the file (s3://bucket-name/path/to/file).

    Outputs
    -------
    exists : bool
        True if the file exists, False otherwise.
    """
    log.info(f"Checking if file exists at {s3_uri}")
    bucket, key = bucket_key_from_uri(s3_uri)
    s3 = boto3.client("s3")

    # Check for any object with the given prefix
    response = s3.list_objects_v2(Bucket=bucket, Prefix=key, MaxKeys=1)
    return "Contents" in response


def s3_ls(s3_uri: str) -> list:
    """
    List all files in an S3 bucket/path.

    Parameters
    ----------
    s3_uri : str
        The S3 URI

    Outputs
    -------
    files : list
        A list of file paths in the S3 bucket/path.
    """
    log.info(f"Listing files in {s3_uri}")
    # Remove the 's3://' prefix and split the path into the bucket name and the key
    bucket, key = bucket_key_from_uri(s3_uri)

    # Create an S3 session
    s3 = boto3.resource("s3")

    # List all files in the S3 bucket/path
    files = [
        f"{bucket}/{obj.key}"
        for obj in s3.Bucket(bucket).objects.filter(Prefix=key)
        if not obj.key.endswith("/")
    ]

    return files
