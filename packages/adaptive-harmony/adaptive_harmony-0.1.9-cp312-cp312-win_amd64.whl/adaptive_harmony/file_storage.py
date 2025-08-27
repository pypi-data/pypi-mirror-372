"""
Pure Python file storage implementation supporting local filesystem and S3.
Based on the Rust file-storage crate API.
"""

import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

try:
    import boto3
    from botocore.exceptions import ClientError

    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


@dataclass
class FileStorageConfig:
    """Configuration for file storage backends."""

    @staticmethod
    def local(path: Union[str, Path]) -> "LocalFileStorageConfig":
        """Create a local filesystem storage configuration."""
        return LocalFileStorageConfig(path=Path(path))

    @staticmethod
    def s3(
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
        region: Optional[str] = None,
        url: Optional[str] = None,
        endpoint: Optional[str] = None,
        force_path_style: bool = False,
    ) -> "S3FileStorageConfig":
        """Create an S3 storage configuration."""
        return S3FileStorageConfig(
            bucket=bucket, prefix=prefix, region=region, url=url, endpoint=endpoint, force_path_style=force_path_style
        )

    @staticmethod
    def from_url(
        url: str,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        force_path_style: bool = False,
    ) -> Union["LocalFileStorageConfig", "S3FileStorageConfig"]:
        """Create a storage configuration from a URL."""
        parsed = urlparse(url)

        if parsed.scheme == "s3":
            # Extract bucket and prefix from s3:// URL
            bucket_from_url = parsed.netloc
            prefix_from_url = parsed.path.lstrip("/")

            return S3FileStorageConfig(
                bucket=bucket or bucket_from_url,
                prefix=prefix or prefix_from_url or None,
                region=region,  # from env ?
                url=url,
                endpoint=endpoint,  # from env ?
                force_path_style=force_path_style,
            )
        elif parsed.scheme in ("file", "") or parsed.scheme is None:
            # Local file path
            path = parsed.path if parsed.scheme == "file" else url
            return LocalFileStorageConfig(path=Path(path))
        else:
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")


@dataclass
class LocalFileStorageConfig(FileStorageConfig):
    """Configuration for local filesystem storage."""

    path: Path


@dataclass
class S3FileStorageConfig(FileStorageConfig):
    """Configuration for S3 storage."""

    bucket: Optional[str] = None
    prefix: Optional[str] = None
    region: Optional[str] = None
    url: Optional[str] = None
    endpoint: Optional[str] = None
    force_path_style: bool = False


class StoredFile:
    """Represents a file stored in the storage backend."""

    def __init__(self, storage: "FileStorage", path: str):
        self.storage = storage
        self.path = path

    def read(self) -> bytes:
        """Read the file content."""
        return self.storage.read(self.path)

    def __str__(self) -> str:
        return self.storage._format_path(self.path)


class FileStorage(ABC):
    """Abstract base class for file storage backends."""

    @staticmethod
    def new(config: FileStorageConfig) -> "FileStorage":
        """Create a new storage instance from configuration."""
        if isinstance(config, LocalFileStorageConfig):
            return LocalFileStorage(config)
        elif isinstance(config, S3FileStorageConfig):
            return S3FileStorage(config)
        else:
            raise ValueError(f"Unsupported config type: {type(config)}")

    @abstractmethod
    def read(self, file_path: str) -> bytes:
        """Read file content and return as bytes."""
        pass

    @abstractmethod
    def write(self, local_file_path: str, destination_path: str) -> str:
        """Write a local file to the storage and return the stored file URL."""
        pass

    @abstractmethod
    def append(self, content: bytes, destination_path: str) -> str:
        """Append content to a file and return the stored file URL."""
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """Check if a file exists in the storage."""
        pass

    @abstractmethod
    def _format_path(self, path: str) -> str:
        """Format a path for display/return."""
        pass


class LocalFileStorage(FileStorage):
    """Local filesystem storage implementation."""

    def __init__(self, config: LocalFileStorageConfig):
        self.base_path = config.path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def read(self, file_path: str) -> bytes:
        """Read file content from local storage."""
        full_path = self._resolve_path(file_path)
        try:
            return full_path.read_bytes()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

    def write(self, local_file_path: str, destination_path: str) -> str:
        """Copy a local file to the storage."""
        src_path = Path(local_file_path)
        dest_path = self._resolve_path(destination_path)

        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(src_path, dest_path)

        return self._format_path(destination_path)

    def append(self, content: bytes, destination_path: str) -> str:
        """Append content to a file in local storage."""
        full_path = self._resolve_path(destination_path)

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Append content
        with open(full_path, "a") as f:
            f.write(content)

        return self._format_path(destination_path)

    def exists(self, file_path: str) -> bool:
        """Check if file exists in local storage."""
        full_path = self._resolve_path(file_path)
        return full_path.exists()

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve a relative file path to absolute path within base directory."""
        # Handle file:// URLs
        if file_path.startswith("file://"):
            file_path = file_path[7:]

        # Handle absolute paths
        if file_path.startswith("/"):
            return Path(file_path)

        return self.base_path / file_path

    def _format_path(self, path: str) -> str:
        """Format path for display."""
        full_path = self._resolve_path(path)
        return f"file://{full_path}"


class S3FileStorage(FileStorage):
    """S3 storage implementation."""

    def __init__(self, config: S3FileStorageConfig):
        if not HAS_BOTO3:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")

        self.config = config

        # Determine bucket and prefix
        if config.url and config.url.startswith("s3://"):
            parsed = urlparse(config.url)
            self.bucket = config.bucket or parsed.netloc
            self.prefix = config.prefix or parsed.path.lstrip("/") or ""
        else:
            if not config.bucket:
                raise ValueError("S3 storage requires either a bucket name or s3:// URL")
            self.bucket = config.bucket
            self.prefix = config.prefix or ""

        # Create S3 client
        session = boto3.Session()

        client_kwargs = {}
        if config.region:
            client_kwargs["region_name"] = config.region
        if config.endpoint:
            client_kwargs["endpoint_url"] = config.endpoint
        if config.force_path_style:
            client_kwargs["config"] = boto3.Config(s3={"addressing_style": "path"})

        self.s3_client = session.client("s3", **client_kwargs)

    def read(self, file_path: str) -> bytes:
        """Read file content from S3."""
        s3_key = self._get_s3_key(file_path)

        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {file_path}")
            raise

    def write(self, local_file_path: str, destination_path: str) -> str:
        """Upload a local file to S3."""
        s3_key = self._get_s3_key(destination_path)

        self.s3_client.upload_file(local_file_path, self.bucket, s3_key)

        return self._format_path(destination_path)

    def append(self, content: bytes, destination_path: str) -> str:
        """Append content to a file in S3 (read-modify-write)."""
        # S3 doesn't support native append, so we need to read-modify-write
        existing_content = b""

        if self.exists(destination_path):
            existing_content = self.read(destination_path)

        # Combine existing content with new content
        combined_content = existing_content + content

        # Write to a temporary file and upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(combined_content)
            temp_file.flush()

            result = self.write(temp_file.name, destination_path)

            # Clean up temp file
            os.unlink(temp_file.name)

            return result

    def exists(self, file_path: str) -> bool:
        """Check if file exists in S3."""
        s3_key = self._get_s3_key(file_path)

        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def _get_s3_key(self, file_path: str) -> str:
        """Convert file path to S3 key."""
        # Handle s3:// URLs
        if file_path.startswith("s3://"):
            parsed = urlparse(file_path)
            if parsed.netloc != self.bucket:
                raise ValueError(f"File path bucket {parsed.netloc} doesn't match configured bucket {self.bucket}")
            return parsed.path.lstrip("/")

        # Combine prefix with file path
        if self.prefix:
            return f"{self.prefix.rstrip('/')}/{file_path.lstrip('/')}"
        return file_path.lstrip("/")

    def _format_path(self, path: str) -> str:
        """Format path for display."""
        s3_key = self._get_s3_key(path)
        return f"s3://{self.bucket}/{s3_key}"
