import logging
import os

import boto3
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_presigned_url(
    bucket_name: str,
    object_name: str,
    expiration: int = 28800,
    url_type: str = "put",
    region_name: str = "eu-central-1",
) -> str:
    """
    Generate a presigned URL for S3 operations.

    Args:
        bucket_name (str): Name of the S3 bucket.
        object_name (str): S3 object name/key.
        expiration (int, optional): Time in seconds before the presigned URL expires. Defaults to 28800 (8 hours).
        url_type (str, optional): Type of URL to generate - 'put' for upload, 'get' for download. Defaults to 'put'.
        region_name (str, optional): AWS region name. Defaults to 'eu-central-1'.

    Returns:
        str: Presigned URL if successful, or error message.
    """  # noqa: E501
    try:
        url_map = {"put": "put_object", "get": "get_object"}
        if url_type not in url_map:
            return f"Error: Invalid URL type: {url_type}. Use 'put' or 'get'."
        action = url_map[url_type]

        aws_config = {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
        }
        aws_config = {k: v for k, v in aws_config.items() if v is not None}

        config = boto3.session.Config(signature_version="s3v4")
        s3_client = boto3.client(
            "s3",
            **aws_config,
            region_name=region_name,
            config=config,
            endpoint_url=f"https://s3.{region_name}.amazonaws.com",
        )

        response = s3_client.generate_presigned_url(
            action,
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
        logger.info(f"Generated {url_type} presigned URL for {bucket_name}/{object_name}")
        return response

    except Exception as e:
        error_msg = f"Error generating presigned URL: {str(e)}"
        logger.error(error_msg)
        return error_msg


def upload_to_url(url: str, file_path: str) -> str:
    """
    Upload a file to a presigned S3 URL.

    Args:
        url (str): The presigned URL for upload.
        file_path (str): Path to the file to upload.

    Returns:
        str: Success or error message.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"

        with open(file_path, "rb") as f:
            response = requests.put(url, data=f, timeout=300)
            response.raise_for_status()

        success_msg = f"Upload successful: {file_path}"
        logger.info(f"Successfully uploaded {file_path}")
        return success_msg

    except requests.RequestException as e:
        error_msg = f"Upload failed: {str(e)}"
        logger.error(f"Failed to upload {file_path}: {str(e)}")
        return error_msg
    except Exception as e:
        error_msg = f"Upload failed: {str(e)}"
        logger.error(f"Unexpected error uploading {file_path}: {str(e)}")
        return error_msg


def download_from_url(url: str, file_name: str) -> str:
    """
    Download a file from a presigned S3 URL.

    Args:
        url (str): The presigned URL for download.
        file_name (str): Name of the file to save locally.

    Returns:
        str: Success or error message.
    """
    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()

        with open(file_name, "wb") as f:
            f.write(response.content)

        success_msg = f"Download successful: {file_name}"
        logger.info(f"Successfully downloaded {file_name}")
        return success_msg

    except requests.RequestException as e:
        error_msg = f"Download failed: {str(e)}"
        logger.error(f"Failed to download {file_name}: {str(e)}")
        return error_msg
    except Exception as e:
        error_msg = f"Download failed: {str(e)}"
        logger.error(f"Unexpected error downloading {file_name}: {str(e)}")
        return error_msg
