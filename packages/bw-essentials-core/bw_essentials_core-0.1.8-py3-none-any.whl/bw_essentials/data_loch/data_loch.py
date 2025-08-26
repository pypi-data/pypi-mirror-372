"""
Module for interacting with LakeFS and S3.

This module defines the `LakeFS` class, which provides a high-level interface for managing
version-controlled data in LakeFS using an underlying S3-compatible object store.

Key Features:
- Upload and download files to/from LakeFS.
- Sync entire directories from LakeFS to local and vice versa.
- Check file existence in LakeFS.
- Commit changes to branches in LakeFS.
- Retrieve the latest or N latest files from a given LakeFS path.
- Delete LakeFS directory paths (prefixes).

Requires:
- `lakefs` client
- `S3Utils` from `bw_essentials.s3_utils`

Intended for automation of LakeFS operations in data pipelines or services.
"""

import concurrent
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from lakefs.client import Client
from bw_essentials.s3_utils.s3_utils import S3Utils

logger = logging.getLogger(__name__)


class DataLoch:
    """
    LakeFS class for managing versioned data operations on LakeFS over S3.
    """

    def __init__(self):
        """
        Initialize a LakeFS instance with S3 and LakeFS client setup.

        Args:
        """
        logger.info("Initializing LakeFS instance")
        self.access_key = self._get_env_var("DATA_LAKE_ACCESS_KEY")
        self.secret_key = self._get_env_var("DATA_LAKE_SECRET_KEY")
        self.host = self._get_env_var("DATA_LAKE_HOST_URL")
        self.client = self._get_lakefs_client()
        self.s3 = S3Utils()

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

    def _get_lakefs_client(self):
        """
        Get LakeFS client.

        Returns:
            lakefs.client.Client: Authenticated LakeFS client.
        """
        logger.info("Initializing LakeFS client")
        return Client(host=self.host, username=self.access_key, password=self.secret_key)

    def _get_branch(self, repository, branch):
        """
        Return LakeFS branch object.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.

        Returns:
            lakefs.Branch: LakeFS branch object.
        """
        from lakefs import Repository
        return Repository(repository, client=self.client).branch(branch_id=branch)

    def _get_meta_data(self, repository, branch):
        """
        Return metadata dictionary for commit operation.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.

        Returns:
            dict: Metadata for commit.
        """
        return {
            'source': os.getcwd(),
            'branch': branch,
            'repository': repository,
            'timestamp': str(datetime.now())
        }

    def upload_data(self, repository, branch, local_file_path, file_name, commit=True):
        """
        Upload a single file to a LakeFS branch and optionally commit the change.

        Args:
            repository (str): LakeFS repository name.
            branch (str): Target branch in the repository.
            local_file_path (str): Full local path of the file to upload.
            file_name (str): File name to use in LakeFS.
            commit (bool): Whether to commit the change after upload. Defaults to True.
        """
        logger.info(f"Uploading {file_name=} from {local_file_path=}")
        logger.info(f"{file_name=} uploading to LakeFS")
        branch_obj = self._get_branch(branch=branch, repository=repository)
        obj = branch_obj.object(path=f"{file_name}")
        with open(local_file_path, mode='rb') as reader, obj.writer("wb") as writer:
            writer.write(reader.read())
        commit_response = branch_obj.commit(
            message=f"{file_name=} uploaded to data lake.",
            metadata=self._get_meta_data(branch=branch,repository=repository)
        )
        logger.info(f"Changes committed: {commit_response=}")

    def download_data(self, repository, branch, local_file_path, file_name):
        """
        Download a single file from a LakeFS branch to a local path.

        Args:
            repository (str): LakeFS repository name.
            branch (str): Branch in the repository.
            local_file_path (str): Full local path to save the file.
            file_name (str): Name of the file in LakeFS.
        """
        logger.info(f"Downloading file {file_name} to {local_file_path}")
        self.s3.download_file(repository, f"{branch}/{file_name}", local_file_path)

    def file_exists(self, repository, branch, filename):
        """
        Check whether a file exists in a LakeFS repository branch.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.
            filename (str): File name to check.

        Returns:
            bool: True if file exists, False otherwise.
        """
        try:
            self.s3.s3_instance.head_object(Bucket=repository, Key=f"{branch}/{filename}")
            return True
        except Exception:
            return False

    def sync_dir(self, repository, branch, server_path, local_path=None):
        """
        Sync a directory from LakeFS (S3) to the local file system.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.
            server_path (str): Path under the branch to sync from.
            local_path (str, optional): Local destination directory. Defaults to current dir.
        """
        logger.info(f"Syncing directory from {server_path} to {local_path}")
        prefix = f"{branch}/{server_path}"
        args = []
        for obj in self.s3.list_bucket_objects(repository, prefix):
            rel_path = os.path.relpath(obj['Key'], prefix)
            target = rel_path if not local_path else os.path.join(local_path, rel_path)
            if os.path.exists(target) or obj['Key'].endswith('/'):
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            args.append((repository, obj['Key'], target))
        with ThreadPoolExecutor(max_workers=4) as executor:
            [executor.submit(self.s3.download_file, repo, key, target) for repo, key, target in args]
        logger.info("Directory sync complete")

    def upload_dir(self, repository, branch, local_path, server_path):
        """
        Upload all files from a local directory to LakeFS and commit them.

        Args:
            repository (str): Repository name.
            branch (str): Target branch.
            local_path (str): Local directory path.
            server_path (str): Target path in LakeFS under the branch.
        """
        logger.info(f"Uploading directory {local_path} to {server_path}")
        directory = Path(local_path)
        args = [
            (repository, branch, str(file), f"{server_path}/{file.name}", False)
            for file in directory.iterdir() if file.is_file()
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            [executor.submit(self.upload_data, repo, br, local, output, commit)
             for repo, br, local, output, commit in args]
        branch_obj = self._get_branch(repository, branch)
        commit_response = branch_obj.commit(
            message=f"{local_path} uploaded to data lake.",
            metadata=self._get_meta_data(repository, branch)
        )
        logger.info(f"Directory uploaded and committed: {commit_response}")

    def get_latest_file(self, repository, branch, server_path, local_file_path):
        """
        Get and download the latest modified file from a LakeFS path.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.
            server_path (str): Path in LakeFS under the branch.
            local_file_path (str): Local destination path to save the file.
        """
        logger.info(f"Fetching latest file from {server_path}")
        prefix = f"{branch}/{server_path}"
        key = self.s3.get_latest_file_by_prefix(repository, prefix)
        if key:
            self.s3.download_file(repository, key, local_file_path)

    def get_latest_n_files(self, repository, branch, server_path, local_file_path, count=1):
        """
        Download the latest N files from a given LakeFS path.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.
            server_path (str): Path in LakeFS under the branch.
            local_file_path (str): Local directory to store downloaded files.
            count (int, optional): Number of recent files to download. Defaults to 1.
        """
        logger.info(f"Fetching latest {count} files from {server_path}")
        prefix = f"{branch}/{server_path}"
        keys = self.s3.get_latest_n_files(repository, prefix, count=count)
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        args = []
        for key in keys:
            rel_path = os.path.relpath(key, prefix)
            target = os.path.join(local_file_path, rel_path)
            if not os.path.exists(target):
                args.append((repository, key, target))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            [executor.submit(self.s3.download_file, repo, key, target) for repo, key, target in args]
        logger.info("Downloaded latest files")

    def delete_dir(self, repository, branch, server_path):
        """
        Delete all files under a given path (prefix) in a LakeFS branch.

        Args:
            repository (str): Repository name.
            branch (str): Branch name.
            server_path (str): Path in LakeFS to delete under the branch.
        """
        logger.info(f"Deleting directory {server_path}")
        prefix = f"{branch}/{server_path}"
        self.s3.delete_files_by_prefix(repository, prefix)
        logger.info(f"Deleted all files under prefix {prefix}")

    def delete_single_file(self, repository: str, branch: str, server_path: str) -> None:
        """
        Delete a single file at the specified path in a LakeFS branch.

        Args:
            repository (str): The name of the LakeFS repository.
            branch (str): The name of the branch within the repository.
            server_path (str): The file path (relative to the branch) to delete.
        """
        full_path = f"{branch}/{server_path}"
        logger.info(f"Attempting to delete file at path: {full_path} in repository: {repository}")

        self.s3.delete_file(repository, full_path)

        logger.info(f"Successfully deleted file: {full_path} from repository: {repository}")
