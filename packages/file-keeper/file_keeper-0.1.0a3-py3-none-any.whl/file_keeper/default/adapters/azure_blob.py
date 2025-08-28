"""Azure Blob Storage adapter."""

from __future__ import annotations

import codecs
import dataclasses
import os
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContainerClient,
    ContentSettings,
    generate_blob_sas,
)
from typing_extensions import override

import file_keeper as fk


@dataclasses.dataclass
class Settings(fk.Settings):
    """Azure Blob Storage settings."""

    account_name: str | None = None
    """Name of the account."""
    account_key: str = ""
    """Key for the account."""

    account_url: str = "https://{account_name}.blob.core.windows.net"
    """Custom resource URL."""
    ## azurite
    # account_url: str = "http://127.0.0.1:10000/{account_name}"

    client: BlobServiceClient = None  # pyright: ignore[reportAssignmentType]
    """Existing storage client."""

    container_name: str = ""
    """Name of the storage container."""

    container: ContainerClient = None  # pyright: ignore[reportAssignmentType]
    """Existing container client."""

    def __post_init__(self, **kwargs: Any):
        super().__post_init__(**kwargs)

        self.path = self.path.lstrip("/")

        if not self.client:
            if self.account_name:
                self.account_url = self.account_url.format(account_name=self.account_name)
                credential = {
                    "account_name": self.account_name,
                    "account_key": self.account_key,
                }
            elif self.account_key:
                credential = self.account_key
            else:
                credential = None

            self.client = BlobServiceClient(
                self.account_url,
                credential,
            )

        self.account_url = self.client.url.rstrip("/")
        self.account_name = self.client.account_name

        if not self.container:
            self.container = self.client.get_container_client(self.container_name)
        self.container_name = self.container.container_name

        if not self.container.exists():
            if self.initialize:
                self.container.create_container()
            else:
                raise fk.exc.InvalidStorageConfigurationError(
                    self.name,
                    f"container `{self.container_name}` does not exist",
                )


class Uploader(fk.Uploader):
    """Azure Blob Storage uploader."""

    storage: AzureBlobStorage
    capabilities = fk.Capability.CREATE

    @override
    def upload(
        self,
        location: fk.Location,
        upload: fk.Upload,
        extras: dict[str, Any],
    ) -> fk.FileData:
        """Upload a file to Azure Blob Storage."""
        filepath = self.storage.full_path(location)
        blob = self.storage.settings.container.get_blob_client(filepath)

        if not self.storage.settings.override_existing and blob.exists():
            raise fk.exc.ExistingFileError(self.storage, location)

        result = blob.upload_blob(
            upload.stream,
            overwrite=True,
            content_settings=ContentSettings(content_type=upload.content_type),
        )

        return fk.FileData(
            location,
            upload.size,
            upload.content_type,
            codecs.encode(result["content_md5"], "hex").decode(),
        )


class Reader(fk.Reader):
    """Azure Blob Storage reader."""

    storage: AzureBlobStorage
    capabilities = fk.Capability.STREAM | fk.Capability.LINK_PERMANENT

    @override
    def stream(self, data: fk.FileData, extras: dict[str, Any]) -> Iterable[bytes]:
        filepath = self.storage.full_path(data.location)

        blob = self.storage.settings.container.get_blob_client(filepath)
        if not blob.exists():
            raise fk.exc.MissingFileError(self.storage, data.location)

        return blob.download_blob().chunks()

    @override
    def permanent_link(self, data: fk.FileData, extras: dict[str, Any]) -> str:
        account_url = self.storage.settings.account_url
        container = self.storage.settings.container
        filepath = self.storage.full_path(data.location)

        return f"{account_url}/{container.container_name}/{filepath}"


class Manager(fk.Manager):
    """Azure Blob Storage manager."""

    storage: AzureBlobStorage
    capabilities = (
        fk.Capability.REMOVE
        | fk.Capability.SIGNED
        | fk.Capability.EXISTS
        | fk.Capability.SCAN
        | fk.Capability.ANALYZE
        | fk.Capability.COPY
        | fk.Capability.MOVE
    )

    @override
    def copy(self, location: fk.Location, data: fk.FileData, extras: dict[str, Any]) -> fk.FileData:
        """Copy a file to a new location."""
        src_filepath = self.storage.full_path(data.location)
        blob = self.storage.settings.container.get_blob_client(src_filepath)
        if not blob.exists():
            raise fk.exc.MissingFileError(self.storage, data.location)

        dest_filepath = self.storage.full_path(location)
        dest = self.storage.settings.container.get_blob_client(dest_filepath)
        if not self.storage.settings.override_existing and dest.exists():
            raise fk.exc.ExistingFileError(self.storage, location)

        account_url = self.storage.settings.account_url
        container_name = self.storage.settings.container_name
        url = f"{account_url}/{container_name}/{src_filepath}"
        dest.start_copy_from_url(url)
        return self.analyze(location, extras)

    @override
    def move(self, location: fk.Location, data: fk.FileData, extras: dict[str, Any]) -> fk.FileData:
        self.copy(location, data, extras)
        self.remove(data, extras)
        return self.analyze(location, extras)

    @override
    def analyze(self, location: fk.Location, extras: dict[str, Any]) -> fk.FileData:
        filepath = self.storage.full_path(location)
        blob = self.storage.settings.container.get_blob_client(filepath)
        if not blob.exists():
            raise fk.exc.MissingFileError(self.storage, location)

        info = blob.get_blob_properties()
        content_info = info["content_settings"]
        return fk.FileData(
            location,
            info["size"],
            content_info["content_type"],
            codecs.encode(content_info["content_md5"], "hex").decode(),
        )

    @override
    def exists(self, data: fk.FileData, extras: dict[str, Any]) -> bool:
        filepath = self.storage.full_path(data.location)
        blob_client = self.storage.settings.container.get_blob_client(filepath)
        return blob_client.exists()

    @override
    def scan(self, extras: dict[str, Any]) -> Iterable[str]:
        path = self.storage.settings.path

        for name in self.storage.settings.container.list_blob_names():
            yield os.path.relpath(name, path)

    @override
    def remove(
        self,
        data: fk.FileData,
        extras: dict[str, Any],
    ) -> bool:
        filepath = self.storage.full_path(data.location)
        blob_client = self.storage.settings.container.get_blob_client(filepath)
        if not blob_client.exists():
            return False

        blob_client.delete_blob()
        return True

    @override
    def signed(self, action: fk.types.SignedAction, duration: int, location: fk.Location, extras: dict[str, Any]):
        perms = {}
        if action == "download":
            perms["read"] = True
        elif action == "upload":
            perms["write"] = True
            perms["create"] = True
        elif action == "delete":
            perms["delete"] = True

        client = self.storage.settings.client
        container = self.storage.settings.container
        filepath = self.storage.full_path(location)

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(seconds=duration)

        sas = generate_blob_sas(
            account_name=client.account_name,  # pyright: ignore[reportArgumentType]
            account_key=self.storage.settings.account_key,
            container_name=container.container_name,
            blob_name=filepath,
            permission=BlobSasPermissions(**perms),
            expiry=expiry_time,
        )
        account_url = self.storage.settings.account_url

        return f"{account_url}/{container.container_name}/{filepath}?{sas}"


class AzureBlobStorage(fk.Storage):
    """Azure Blob Storage adapter."""

    settings: Settings
    SettingsFactory = Settings
    UploaderFactory = Uploader
    ManagerFactory = Manager
    ReaderFactory = Reader
