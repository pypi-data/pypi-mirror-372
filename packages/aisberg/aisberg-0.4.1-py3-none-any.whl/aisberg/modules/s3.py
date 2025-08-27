import io
import logging
import mimetypes
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# -------- Progress Bar --------
class ProgressPercentage:
    def __init__(self, file_size, object_name, bar_length=30, verbose=False):
        """
        Initialize the ProgressPercentage class.
        """
        self._file_size = file_size / 1024 / 1024  # MB
        self._seen_so_far = 0
        self._object_name = object_name
        self._bar_length = bar_length
        self._verbose = verbose

    def __call__(self, bytes_amount):
        if not self._verbose:
            return

        self._seen_so_far += bytes_amount / 1024 / 1024  # MB
        percentage = (self._seen_so_far / self._file_size) * 100
        bar_filled_length = int(self._bar_length * self._seen_so_far // self._file_size)
        bar = "█" * bar_filled_length + "-" * (self._bar_length - bar_filled_length)
        sys.stdout.write(
            f"\r{self._object_name}: |{bar}| {self._seen_so_far:.2f} MB / "
            f"{self._file_size:.2f} MB ({percentage:.2f}%)"
        )
        sys.stdout.flush()
        if self._seen_so_far >= self._file_size:
            sys.stdout.write("\n")
            sys.stdout.flush()


# -------- Base S3Module --------
class BaseS3Module(ABC):
    """
    Base abstraite pour modules S3.
    """

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        endpoint_url: Optional[str] = None,
        region_name: str = "fr-par",
        verbose: bool = False,
    ):
        self._args = dict(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )
        self._verbose = verbose

    @abstractmethod
    def _get_client(self):
        """Returns the S3 client."""
        ...

    @staticmethod
    def _prepare_metadata(file, metadata=None):
        """Prepare metadata for the file.

        Args:
            file (str | io.BytesIO): path to the file or a BytesIO object.
            metadata (dict, optional): Additional metadata to enrich the file information.

        Returns:
            tuple: (file_size (int), metadata (dict)) with enriched file information.
        """
        if metadata is None:
            metadata = {}

        if isinstance(file, str):
            file_size = os.path.getsize(file)
            file_type, _ = mimetypes.guess_type(file)
            file_creation_time = datetime.fromtimestamp(
                os.path.getctime(file)
            ).isoformat()
            file_name = os.path.basename(file)
            metadata.update(
                {
                    "FileName": file_name,
                    "FileSize": f"{file_size / (1024 * 1024):.2f} MB",
                    "FileType": file_type or "application/octet-stream",
                    "CreationTime": file_creation_time,
                }
            )
        else:
            file.seek(0, io.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            metadata.update(
                {
                    "FileSize": f"{file_size / (1024 * 1024):.2f} MB",
                    "FileType": "application/octet-stream",
                    "CreationTime": datetime.now().isoformat(),
                }
            )
        return file_size, metadata

    @staticmethod
    def _get_object_name(file, object_name):
        return object_name or (file if isinstance(file, str) else "default_object_name")

    @abstractmethod
    def upload_file(
        self,
        file: Union[str, io.BytesIO],
        bucket_name: str,
        object_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Any:
        """
        Uploads a file to the S3 bucket.

        Args:
            file (str or BytesIO): The file to upload. Can be a path to a file or a BytesIO object.
            bucket_name (str): The name of the S3 bucket.
            object_name (str, optional): The object name in S3. Defaults to filename if not provided.
            metadata (dict, optional): Additional metadata for the object.

        Returns:
            Any: True if the upload succeeded, else False or raises an exception.
        """
        ...

    @abstractmethod
    def download_file(
        self,
        bucket_name: str,
        object_name: str,
        save_to: Optional[str] = None,
    ) -> Any:
        """
        Downloads a file from the S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            object_name (str): The object name in S3.
            save_to (str, optional): Local path to save the file. If not provided, returns file content as BytesIO.

        Returns:
            Any: True if the file was saved locally, else a BytesIO object with file content, or False on failure.
        """
        ...

    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str) -> Any:
        """
        Deletes a file from the S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            object_name (str): The object name in S3.

        Returns:
            Any: True if the file was deleted, False otherwise.
        """
        ...

    @abstractmethod
    def list_files(self, bucket_name: str) -> Any:
        """
        Lists all files in the specified S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.

        Returns:
            Any: List of object names (keys) in the bucket, or an empty list on failure.
        """
        ...

    @abstractmethod
    def list_buckets(self) -> Any:
        """
        Lists all buckets accessible by the credentials.

        Returns:
            Any: List of bucket names, or an empty list on failure.
        """
        ...


# -------- Sync --------
class SyncS3Module(BaseS3Module):
    def _get_client(self):
        try:
            import boto3

            return boto3.client("s3", **self._args)
        except ImportError:
            logger.error(
                "boto3 is not installed. Please install it to use S3 functionalities."
            )
            raise ImportError("boto3 is required for S3 operations.")
        except Exception as e:
            logger.error(f"Failed to create S3 client: {e}")
            raise RuntimeError("Failed to create S3 client.") from e

    def upload_file(self, file, bucket_name, object_name=None, metadata=None) -> bool:
        s3 = self._get_client()
        object_name = self._get_object_name(file, object_name)
        file_size, metadata = self._prepare_metadata(file, metadata)
        progress_callback = ProgressPercentage(
            file_size, object_name, verbose=self._verbose
        )
        from boto3.s3.transfer import TransferConfig

        config = TransferConfig(use_threads=False)
        extra_args = {"Metadata": metadata}

        try:
            if isinstance(file, str):
                s3.upload_file(
                    file,
                    bucket_name,
                    object_name,
                    Config=config,
                    Callback=progress_callback,
                    ExtraArgs=extra_args,
                )
            else:
                s3.upload_fileobj(
                    file,
                    bucket_name,
                    object_name,
                    Config=config,
                    Callback=progress_callback,
                    ExtraArgs=extra_args,
                )
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
        return True

    def download_file(self, bucket_name, object_name, save_to=None):
        s3 = self._get_client()
        from boto3.s3.transfer import TransferConfig

        try:
            obj = s3.head_object(Bucket=bucket_name, Key=object_name)
            file_size = obj["ContentLength"]
            progress_callback = ProgressPercentage(
                file_size, object_name, verbose=self._verbose
            )
            config = TransferConfig(use_threads=False)

            if self._verbose:
                print(
                    f"Downloading {object_name} from bucket {bucket_name} "
                    f"({file_size / (1024 * 1024):.2f} MB)"
                )

            if save_to:
                s3.download_file(
                    bucket_name,
                    object_name,
                    save_to,
                    Config=config,
                    Callback=progress_callback,
                )
                return True
            else:
                file_obj = io.BytesIO()
                s3.download_fileobj(
                    bucket_name,
                    object_name,
                    file_obj,
                    Config=config,
                    Callback=progress_callback,
                )
                file_obj.seek(0)
                return file_obj
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

    def delete_file(self, bucket_name, object_name):
        s3 = self._get_client()
        try:
            s3.delete_object(Bucket=bucket_name, Key=object_name)
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    def list_files(self, bucket_name):
        s3 = self._get_client()
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []

    def list_buckets(self):
        s3 = self._get_client()
        try:
            response = s3.list_buckets()
            return [bucket["Name"] for bucket in response.get("Buckets", [])]
        except Exception as e:
            logger.error(f"List buckets failed: {e}")
            return []
