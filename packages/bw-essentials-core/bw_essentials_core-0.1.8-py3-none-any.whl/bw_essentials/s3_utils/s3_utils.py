"""
Module for interacting with AWS S3.

This module contains the S3Utils class, which provides utility functions for:
- Uploading and downloading files
- Listing objects
- Reading content
- Moving and deleting files
- Checking file existence

Supports custom S3 endpoints (e.g., for localstack or MinIO).
"""

import logging
import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
from typing import Optional, List

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Utils:
    """
    Utility class for managing AWS S3 operations.
    """

    def __init__(self):
        """
        Initialize S3Utils instance with AWS credentials.

        Args:
        """
        self.access_key = self._get_env_var("S3_ACCESS_KEY")
        self.secret_key = self._get_env_var("S3_SECRET_KEY")
        self.endpoint_url = self._get_env_var("S3_ENDPOINT_URL")
        self.s3_instance = self._get_s3_instance()

    def _get_env_var(self, key: str) -> str:
        """
        Fetch a required variable from bw_config.py located in the root directory.

        Raises:
            FileNotFoundError: If bw_config.py is not found.
            AttributeError: If the requested key is not defined in the config.

        Returns:
            str: The value of the config variable.
        """
        config_path = os.path.join(os.getcwd(), "bw_config.py")

        if not os.path.exists(config_path):
            raise FileNotFoundError("`bw_config.py` file not found in the root directory. "
                                    "Please ensure the config file exists.")

        spec = spec_from_file_location("bw_config", config_path)
        bw_config = module_from_spec(spec)
        sys.modules["bw_config"] = bw_config
        spec.loader.exec_module(bw_config)

        if not hasattr(bw_config, key):
            raise AttributeError(f"`{key}` not found in bw_config.py. Please define it in the config.")

        return getattr(bw_config, key)

    def _get_s3_instance(self):
        """
        Create and return a boto3 S3 client instance.
        """
        try:
            logger.info("Initializing S3 client instance")
            return boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url
            )
        except Exception as exp:
            logger.error("Error getting S3 client", exc_info=exp)
            raise

    def download_file(self, bucket_name: str, file_key: str, local_path: str):
        """
        Download a file from S3 to a local path.

        Args:
            bucket_name (str): Name of the S3 bucket.
            file_key (str): Key of the file in S3.
            local_path (str): Destination path on the local system.
        """
        try:
            if not file_key or not local_path:
                raise ValueError("file_key and local_path are required.")
            logger.info(f"Downloading {file_key=} to {local_path=}")
            self.s3_instance.download_file(bucket_name, file_key, local_path)
        except Exception as e:
            logger.error("Error downloading file", exc_info=e)
            raise

    def upload_file(self, bucket_name: str, path_to_file: str, object_name: str, content_type: str):
        """
        Upload a local file to an S3 bucket.

        Args:
            bucket_name (str): Target S3 bucket.
            path_to_file (str): Local file path.
            object_name (str): Destination object key in S3.
            content_type (str): MIME type of the file.
        """
        logger.info(f"Uploading file: {path_to_file=} to {bucket_name}/{object_name=} with {content_type=}")
        try:
            with open(path_to_file, 'rb') as file_object:
                self.s3_instance.put_object(
                    Bucket=bucket_name,
                    Key=object_name,
                    Body=file_object,
                    ContentType=content_type
                )
            logger.info("Upload successful")
        except Exception as e:
            logger.error("Error uploading file", exc_info=e)
            raise

    def list_files(self, bucket_name: str, prefix: Optional[str] = "") -> List[str]:
        """
        List files in a bucket under a given prefix.

        Args:
            bucket_name (str): S3 bucket name.
            prefix (Optional[str]): Prefix filter for keys.

        Returns:
            List[str]: List of file keys.
        """
        try:
            response = self.s3_instance.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            files = [item['Key'] for item in response.get('Contents', [])]
            logger.info(f"Found {len(files)} files in {bucket_name}/{prefix}")
            return files
        except Exception as e:
            logger.error("Error listing files", exc_info=e)
            raise

    def list_bucket_objects(
        self, bucket_name: str, filter_prefix: str = "", continuation_token: Optional[str] = None
    ) -> List[dict]:
        """
        Recursively list all objects in a bucket under a given prefix.

        Args:
            bucket_name (str): S3 bucket name.
            filter_prefix (str): Prefix filter for keys.
            continuation_token (Optional[str]): Token for pagination.

        Returns:
            List[dict]: List of object metadata.
        """
        logger.info(f"Listing objects in {bucket_name=} with {filter_prefix=}")
        all_objects = []
        params = {
            'Bucket': bucket_name,
            'Prefix': filter_prefix
        }

        if continuation_token:
            params['ContinuationToken'] = continuation_token

        try:
            response = self.s3_instance.list_objects_v2(**params)
            if 'Contents' in response:
                all_objects.extend(response['Contents'])
                next_token = response.get('NextContinuationToken')
                if next_token:
                    all_objects.extend(self.list_bucket_objects(bucket_name, filter_prefix, next_token))
            return all_objects
        except Exception as e:
            logger.error("Error listing bucket objects", exc_info=e)
            raise

    def delete_file(self, bucket_name: str, file_key: str):
        """
        Delete a file from an S3 bucket.

        Args:
            bucket_name (str): Name of the S3 bucket.
            file_key (str): Key of the file to delete.
        """
        try:
            self.s3_instance.delete_object(Bucket=bucket_name, Key=file_key)
            logger.info(f"Deleted {file_key} from {bucket_name}")
        except Exception as e:
            logger.error("Error deleting file", exc_info=e)
            raise

    def delete_files_by_prefix(self, bucket_name: str, prefix: str):
        """
        Delete all files in a bucket under a given prefix.

        Args:
            bucket_name (str): Name of the S3 bucket.
            prefix (str): Prefix to filter files to delete.
        """
        try:
            objects = self.list_files(bucket_name, prefix)
            if not objects:
                logger.info("No files to delete.")
                return
            delete_payload = {'Objects': [{'Key': key} for key in objects]}
            self.s3_instance.delete_objects(Bucket=bucket_name, Delete=delete_payload)
            logger.info(f"Deleted {len(objects)} files under prefix {prefix}")
        except Exception as e:
            logger.error("Error deleting files by prefix", exc_info=e)
            raise

    def get_latest_file_by_prefix(self, bucket_name: str, prefix: str) -> Optional[str]:
        """
        Get the latest modified file under a specific prefix.

        Args:
            bucket_name (str): Name of the S3 bucket.
            prefix (str): Prefix to filter files.

        Returns:
            Optional[str]: Key of the latest file or None.
        """
        try:
            response = self.s3_instance.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            contents = response.get('Contents', [])
            if not contents:
                logger.info("No files found under prefix.")
                return None
            latest = max(contents, key=lambda x: x['LastModified'])
            logger.info(f"Latest file under {prefix} is {latest['Key']}")
            return latest['Key']
        except Exception as e:
            logger.error("Error getting latest file by prefix", exc_info=e)
            raise

    def file_exists(self, bucket_name: str, file_key: str) -> bool:
        """
        Check if a file exists in an S3 bucket.

        Args:
            bucket_name (str): Name of the S3 bucket.
            file_key (str): Key of the file.

        Returns:
            bool: True if file exists, False otherwise.
        """
        try:
            self.s3_instance.head_object(Bucket=bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            logger.error("Error checking file existence", exc_info=e)
            raise

    def read_file_content(self, bucket_name: str, file_key: str, encoding: str = "utf-8") -> str:
        """
        Read content of a file from S3.

        Args:
            bucket_name (str): S3 bucket name.
            file_key (str): File key in the bucket.
            encoding (str): Encoding format for content.

        Returns:
            str: File content as string.
        """
        try:
            obj = self.s3_instance.get_object(Bucket=bucket_name, Key=file_key)
            content = obj['Body'].read().decode(encoding)
            return content
        except Exception as e:
            logger.error("Error reading file content", exc_info=e)
            raise

    def move_file(self, bucket_name: str, file_key: str, new_file_key: str):
        """
        Move a file within an S3 bucket (copy + delete).

        Args:
            bucket_name (str): S3 bucket name.
            file_key (str): Source key.
            new_file_key (str): Destination key.
        """
        try:
            copy_source = {'Bucket': bucket_name, 'Key': file_key}
            self.s3_instance.copy_object(Bucket=bucket_name, CopySource=copy_source, Key=new_file_key)
            self.s3_instance.delete_object(Bucket=bucket_name, Key=file_key)
            logger.info(f"Moved file from {file_key} to {new_file_key} in {bucket_name}")
        except Exception as e:
            logger.error("Error moving file", exc_info=e)
            raise

    def get_latest_n_files(self, bucket: str, prefix: str, count: int) -> List[str]:
        """
        Get the latest `n` files from the given prefix, sorted by LastModified.

        Args:
            bucket (str): Name of the S3 bucket.
            prefix (str): S3 prefix (folder path).
            count (int): Number of latest files to return.

        Returns:
            List[str]: List of S3 keys for the latest files.
        """
        try:
            paginator = self.s3_instance.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

            all_files = []
            for page in page_iterator:
                contents = page.get("Contents", [])
                all_files.extend(contents)

            sorted_files = sorted(all_files, key=lambda x: x["LastModified"], reverse=True)
            latest_keys = [obj["Key"] for obj in sorted_files[:count]]

            logger.info("Retrieved latest %d files from prefix %s", count, prefix)
            return latest_keys
        except Exception as e:
            logger.error("Failed to get latest files from S3", exc_info=e)
            raise

    @staticmethod
    def get_object_url(bucket_name: str, object_name: str) -> str:
        """
        Generate a public URL for an object in an S3 bucket.

        Args:
            bucket_name (str): Name of the S3 bucket.
            object_name (str): Key of the object.

        Returns:
            str: Public object URL.
        """
        return f"https://{bucket_name}.s3.amazonaws.com/{object_name}"

    def generate_presigned_url(self, bucket_name, object_key, expiration):
        """
        Generate a presigned URL to share an S3 object.
        :param bucket_name: str - your S3 bucket name
        :param object_key: str - the full path of the file in the bucket
        :param expiration: int - time in seconds for the presigned URL to remain valid (default: 1 hour)
        :return: str - presigned URL
        """
        pre_signed_url = self.s3_instance.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )

        return pre_signed_url
