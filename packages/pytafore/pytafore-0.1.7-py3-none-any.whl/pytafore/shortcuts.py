import io
import logging
import pickle

import awswrangler as wr

from .s3 import read_file, upload_content

log = logging.getLogger("local")


def pickle_from_s3(s3_uri):
    """
    Load and return a Python object from a pickle file stored in S3.

    Inputs:
    -------
    s3_uri : str
        The S3 URI of the pickle file to load w or wo the "s3://" prefix.

    Outputs:
    --------
    object
        The deserialized Python object loaded from the pickle file.
    """
    content = read_file(s3_uri=s3_uri, encoding=None)
    buffer = io.BytesIO(content)
    content = pickle.load(buffer)

    return content


def pickle_to_s3(content, s3_uri):
    """
    Serialize a Python object and upload it as a pickle file to S3.

    Parameters
    ----------
    content : object
        The Python object to serialize and store.
    s3_uri : str
        The S3 URI where the pickle file will be uploaded w or wo the "s3://"
        prefix.
    """
    content = pickle.dumps(content)
    upload_content(content, s3_uri, encoding=None)


def csv_to_s3(
    df,
    s3_uri,
    quiet=True,
    **kwargs,
):
    """
    Upload a pandas DataFrame to an S3 URI in CSV format using using
    awswrangler.s3.to_csv.

    Inputs:
    -------
    df : pandas.DataFrame
        The DataFrame to upload.
    s3_uri : str
        The destination S3 URI where the CSV will be saved, w or wo the "s3://"
        prefix.
    quiet : Bool, default = True
        When False, log dataframe shape, size (MB) and S3 URI destination.
    **kwargs :
        Additional keyword arguments passed to awswrangler.s3.to_csv, such as
        header, index, sep, compression, etc.

    Outputs:
    --------
    s3_uri : str
        The S3 URI where the CSV was uploaded, including "s3://".
    """

    if not quiet:
        size_bytes = df.memory_usage(deep=True).sum()
        size_mb = size_bytes / (1024**2)
        log.info(
            f"Uploading DataFrame -- {df.shape[0]} rows, {size_mb:.2f} MB -- to S3: {s3_uri}."
        )

    if not s3_uri.startswith("s3://"):
        s3_uri = f"s3://{s3_uri}"

    wr.s3.to_csv(df=df, path=s3_uri, **kwargs)

    return s3_uri


def csv_from_s3(
    s3_uri,
    quiet=True,
    **kwargs,
):
    """
    Read a CSV file from an S3 URI into a pandas DataFrame using
    awswrangler.s3.read_csv.

    Inputs:
    -------
    s3_uri : str
        The S3 URI of the CSV file to readn w or wo the "s3://" prefix.
    quiet : Bool, default = True
        When False, log S3 URI of read csv.
    **kwargs :
        Additional keyword arguments passed to awswrangler.s3.read_csv, such as
        header, index_col, sep, etc.

    Outputs:
    --------
    pandas.DataFrame
        The DataFrame read from the CSV file stored in S3.
    """
    if not quiet:
        log.info(f"Reading csv to DataFrame from S3: {s3_uri}.")

    if not s3_uri.startswith("s3://"):
        s3_uri = f"s3://{s3_uri}"

    df = wr.s3.read_csv(path=s3_uri, **kwargs)

    return df
