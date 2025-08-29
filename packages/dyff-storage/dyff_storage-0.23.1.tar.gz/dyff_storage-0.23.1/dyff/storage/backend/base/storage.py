# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
from typing import BinaryIO, Iterable, Optional

from dyff.schema.platform import Artifact, ArtifactURL, Entities, StorageSignedURL


class StorageBackend(abc.ABC):
    @abc.abstractmethod
    def storage_size(self, path: str) -> int:
        """Get the total size, in bytes, of all objects stored under the ``path``
        prefix."""

    @abc.abstractmethod
    def list_dir(self, path: str, *, recursive: bool = False) -> Iterable[str]:
        """Get the absolute paths of all objects that are immediate "children" of
        ``path``."""

    @abc.abstractmethod
    def download_recursive(self, source: str, destination: str) -> None:
        """Download all objects stored under the path ``source`` to under the local
        directory ``destination``.

        The directory structure is preserved.
        """

    @abc.abstractmethod
    def upload_recursive(self, source: str, destination: str) -> None:
        """Upload all files stored under the local directory ``source`` to under the
        storage path ``destination``.

        The directory structure is preserved.
        """

    @abc.abstractmethod
    def put_object(self, data: bytes | BinaryIO, destination: str) -> None:
        """Upload a single object in memory."""

    @abc.abstractmethod
    def get_object(self, source: str) -> BinaryIO:
        """Download a single object."""

    @abc.abstractmethod
    def delete_object(self, destination: str) -> None:
        """Delete a single object."""

    @abc.abstractmethod
    def delete_tree(self, destination: str) -> None:
        """Delete the directory tree rooted at 'destination'."""

    @abc.abstractmethod
    def signed_url_for_artifact_upload(
        self,
        artifact: Artifact,
        storage_path: str,
        *,
        size_limit_bytes: Optional[int] = None,
    ) -> StorageSignedURL:
        """Create a temporary signed URL that can be used in a PUT request to upload an
        ``Artifact`` directly to storage."""

    @abc.abstractmethod
    def signed_url_for_dataset_upload(
        self,
        dataset_id: str,
        artifact: Artifact,
        *,
        size_limit_bytes: Optional[int] = None,
        storage_path: Optional[str] = None,
    ) -> StorageSignedURL:
        """Create a temporary signed URL that can be used in a PUT request to upload an
        ``Artifact`` directly to storage."""

    @abc.abstractmethod
    def artifact_downlinks(
        self, entity_kind: Entities, entity_id: str
    ) -> Iterable[ArtifactURL]:
        """Create a list of temporary URLs that can be used in GET requests to download
        all of the artifacts associated with an entity."""

    @abc.abstractmethod
    def logs_downlink(
        self, entity_kind: Entities, entity_id: str
    ) -> Optional[ArtifactURL]:
        """Create a temporary URL that can be used in GET requests to download the logs
        file associated with an entity."""

    @abc.abstractmethod
    def object_md5hash(self, storage_path: str) -> bytes:
        """Compute the MD5 hash of an object in storage."""

    def artifact_md5hash(self, artifact: Artifact, storage_path: str) -> bytes:
        return self.object_md5hash(f"{storage_path}/{artifact.path}")

    @abc.abstractmethod
    def dataset_artifact_md5hash(
        self, dataset_id: str, artifact_path: str, *, storage_path: Optional[str] = None
    ) -> bytes:
        """Compute the MD5 hash of a dataset artifact in storage."""
