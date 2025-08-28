from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import BinaryIO, Generator, Optional

import grpc

from remotivelabs.broker._generated import common_pb2, system_api_pb2
from remotivelabs.broker.client import BrokerClientConnection
from remotivelabs.broker.exceptions import BrokerError

_logger = logging.getLogger(__name__)


def sha256(path: Path) -> str:
    with open(path, "rb") as f:
        b = f.read()
    return hashlib.sha256(b).hexdigest()


class AsyncBrokerFileClient(BrokerClientConnection):
    """
    Client for file operations.
    """

    async def load_configuration(self, folder: Path) -> None:
        """
        Load a new configuration from a directory.

        Args:
            folder: The directory containing the configuration files.
        """
        await self.upload_folder(folder)

        res = await self._system_service.ReloadConfiguration(common_pb2.Empty(), timeout=60000)
        if res.errorMessage:
            raise BrokerError(f"failed to reload broker configuration: {res.errorMessage}")

        _logger.debug("broker configuration reloaded")

    async def upload_folder(self, folder: Path, remote_path: Path | None = None) -> None:
        """Upload a directory and its content to Broker remote storage"""
        files = [f for f in folder.rglob("*") if f.is_file()]
        if not files:
            raise ValueError(f"folder {folder} is empty or does not exist")

        for file in files:
            path_relative_to_folder = file.relative_to(folder)
            target = remote_path / path_relative_to_folder if remote_path else path_relative_to_folder
            await self.upload_file(file, target)

        _logger.debug(f"all files in folder {folder} uploaded to {remote_path}")

    # TODO: Move to another client?
    async def upload_file(self, path: Path, remote_path: Optional[Path] = None) -> Path:
        """Upload a file to to Broker remote storage"""
        remote_path = remote_path if remote_path else Path(path.name)

        if not path.exists() or not path.is_file():
            raise ValueError(f"failed to upload file; invalid file path {path}")

        # TODO: Needed?
        # remote_path.replace(ntpath.sep, posixpath.sep)

        digest = sha256(path)

        with open(path, "rb") as file:
            uploader = multipart_uploader(file, remote_path, 1000000, digest)
            response = await self._system_service.UploadFile(uploader, compression=grpc.Compression.Gzip)

        if response.errorMessage:
            raise BrokerError(f"file upload failed: {response.errorMessage}")

        if response.cancelled:
            raise BrokerError(f"file upload of {path} cancelled")

        _logger.debug(f"file uploaded to {remote_path}")
        return remote_path

    async def download_file(self, remote_path: Path, path: Optional[Path] = None) -> Path:
        """Download a file from Broker remote storage"""
        path = path if path else Path(remote_path.name)

        if path.exists():
            raise ValueError(f"failed to download file to {path}; target exists")

        # TODO: Needed?
        # remote_path.replace(ntpath.sep, posixpath.sep)

        with open(path, "wb") as file:
            async for response in self._system_service.BatchDownloadFiles(
                system_api_pb2.FileDescriptions(fileDescriptions=[system_api_pb2.FileDescription(path=str(remote_path))])
            ):
                if response.errorMessage:
                    raise BrokerError(f"Error downloading file: {response.errorMessage}")
                file.write(response.chunk)

        return path


def multipart_uploader(
    file: BinaryIO, dest_path: Path, chunk_size: int, digest: str
) -> Generator[system_api_pb2.FileUploadRequest, None, None]:
    file_description = system_api_pb2.FileDescription(sha256=digest, path=str(dest_path))
    yield system_api_pb2.FileUploadRequest(fileDescription=file_description)

    while True:
        buf = file.read(chunk_size)
        if not buf:
            return  # return signals end of sequence
        yield system_api_pb2.FileUploadRequest(chunk=buf)
