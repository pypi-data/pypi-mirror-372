# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# mypy: disable-error-code="import-untyped"
import functools
from typing import BinaryIO, Iterable, Optional

from dyff.schema.platform import Artifact, ArtifactURL, Entities, StorageSignedURL
from dyff.storage import dynamic_import, paths
from dyff.storage.backend.base.storage import StorageBackend
from dyff.storage.config import config


@functools.lru_cache()
def _get_backend() -> StorageBackend:
    return dynamic_import.instantiate(config.storage.backend)


def storage_size(path: str) -> int:
    return _get_backend().storage_size(path)


def list_dir(path: str, *, recursive: bool = False) -> Iterable[str]:
    return _get_backend().list_dir(path, recursive=recursive)


def download_recursive(source: str, destination: str) -> None:
    return _get_backend().download_recursive(source, destination)


def upload_recursive(source: str, destination: str) -> None:
    return _get_backend().upload_recursive(source, destination)


def put_object(data: bytes | BinaryIO, destination: str) -> None:
    return _get_backend().put_object(data, destination)


def get_object(source: str) -> BinaryIO:
    return _get_backend().get_object(source)


def delete_object(destination: str) -> None:
    return _get_backend().delete_object(destination)


def delete_tree(destination: str) -> None:
    return _get_backend().delete_tree(destination)


def signed_url_for_artifact_upload(
    artifact: Artifact,
    storage_path: str,
    *,
    size_limit_bytes: Optional[int] = None,
) -> StorageSignedURL:
    return _get_backend().signed_url_for_artifact_upload(
        artifact,
        storage_path,
        size_limit_bytes=size_limit_bytes,
    )


def signed_url_for_dataset_upload(
    dataset_id: str,
    artifact: Artifact,
    *,
    size_limit_bytes: Optional[int] = None,
    storage_path: Optional[str] = None,
) -> StorageSignedURL:
    return _get_backend().signed_url_for_dataset_upload(
        dataset_id,
        artifact,
        size_limit_bytes=size_limit_bytes,
        storage_path=storage_path,
    )


def artifact_downlinks(entity_kind: Entities, entity_id: str) -> Iterable[ArtifactURL]:
    return _get_backend().artifact_downlinks(entity_kind, entity_id)


def logs_downlink(entity_kind: Entities, entity_id: str) -> Optional[ArtifactURL]:
    return _get_backend().logs_downlink(entity_kind, entity_id)


def object_md5hash(storage_path: str) -> bytes:
    return _get_backend().object_md5hash(storage_path)


def artifact_md5hash(artifact: Artifact, storage_path: str) -> bytes:
    return _get_backend().artifact_md5hash(artifact, storage_path)


def dataset_artifact_md5hash(
    dataset_id: str, artifact_path: str, *, storage_path: Optional[str] = None
) -> bytes:
    return _get_backend().dataset_artifact_md5hash(
        dataset_id, artifact_path, storage_path=storage_path
    )


__all__ = [
    "paths",
    "artifact_downlinks",
    "artifact_md5hash",
    "dataset_artifact_md5hash",
    "download_recursive",
    "get_object",
    "list_dir",
    "object_md5hash",
    "put_object",
    "signed_url_for_artifact_upload",
    "signed_url_for_dataset_upload",
    "storage_size",
    "upload_recursive",
]
