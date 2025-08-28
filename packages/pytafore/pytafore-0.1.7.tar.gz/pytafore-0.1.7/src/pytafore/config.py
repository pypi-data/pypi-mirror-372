import logging
from os import environ

import boto3
import requests
from requests_aws4auth import AWS4Auth

log = logging.getLogger("config")


def get_aws_creds(service, region="us-east-1") -> AWS4Auth:
    """
    Set up AWS credentials using boto3 and return AWS4Auth for authentication.

    Parameters
    ----------
    service: str
        What AWS service are we trying to connect to
    region: str
        The AWS region to get the credentials for

    Returns
    -------
    AWS4Auth
        AWS4Auth object for authenticating requests to OpenSearch.
    """
    session = boto3.Session()
    credentials = session.get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        "us-east-1",  # Change to your OpenSearch domain's region
        "es",  # Use 'aoss' for Amazon OpenSearch Service
        session_token=credentials.token,  # Optional, for temporary credentials (e.g., when using AWS STS)
    )
    return auth


def get_execution_role():
    """
    Retrieve the IAM role ARN associated with the current execution context.
    """
    try:
        # Check if running inside SageMaker
        response = requests.get(
            "http://169.254.169.254/latest/meta-data/instance-id", timeout=1
        )

        # Use SageMaker client to get the notebook instance role
        sagemaker_client = boto3.client("sagemaker")
        response = sagemaker_client.list_notebook_instances()
        for notebook_instance in response["NotebookInstances"]:
            if notebook_instance["NotebookInstanceStatus"] == "InService":
                details = sagemaker_client.describe_notebook_instance(
                    NotebookInstanceName=notebook_instance["NotebookInstanceName"]
                )
                return details["RoleArn"]

        raise Exception("No active SageMaker notebook instance found.")

    except Exception:
        # Fallback to STS
        sts_client = boto3.client("sts")
        arn = sts_client.get_caller_identity()["Arn"]
        if "assumed-role" in arn:
            account_id = sts_client.get_caller_identity()["Account"]
            role_name = arn.split("/")[-2]
            return f"arn:aws:iam::{account_id}:role/{role_name}"
        return arn


def get_role() -> str:
    """
    Get the execution role. If there is an issue get the fallback role from env
    """
    try:
        # Try to get the execution role
        role = get_execution_role()
        log.info(f"Role is {role}")
    except Exception:
        # If getting the execution role fails, fallback to the IAM_ROLE environment variable
        role = environ.get("IAM_ROLE")
        log.info(f"Fallback to environment {role}")
    # Return the role
    return role


def log_to_file(path: str, level: int = logging.INFO) -> None:
    """
    Configures the logging module to log messages to a file and to the console.

    Parameters
    ----------
    path : str
        The path to the log file.
    level : int
        The minimum logging level. Default is logging.INFO.
    """
    # noinspection PyArgumentList
    logging.basicConfig(
        # Format of the log message
        format="%(asctime)s %(process)6d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        # Minimum logging level
        level=level,
        handlers=[
            # Handler for writing log messages to a file
            logging.FileHandler(filename=path, mode="a", encoding="utf-8", delay=False),
            # Handler for writing log messages to the console
            logging.StreamHandler(),  # sys.stderr by default, in case you want to test 2>/dev/null
        ],
    )
