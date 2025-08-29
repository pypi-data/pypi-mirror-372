# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import base64
import datetime
from pathlib import Path
from typing import Optional, Tuple

import google.auth.compute_engine
import google.auth.transport.requests
import google.cloud.storage as gcs
from google.cloud.storage import transfer_manager

from dyff.schema.dataset import max_artifact_size_bytes
from dyff.schema.platform import Artifact, StorageSignedURL
from dyff.storage import paths
from dyff.storage.backend.base.storage import StorageBackend


def _bucket_name_from_path(path: str) -> str:
    return _split_bucket_path(path)[0]


def _drop_protocol(path: str) -> str:
    protocol = "gs://"
    if path.startswith(protocol):
        path = path[len(protocol) :]
    return path


def _split_bucket_path(path: str) -> Tuple[str, str]:
    path = _drop_protocol(path)
    parts = path.split("/")
    return parts[0], "/".join(parts[1:])


class GCloudStorageBackend(StorageBackend):
    def storage_size(self, path: str) -> int:
        bucket, prefix = _split_bucket_path(path)
        client = gcs.Client()
        bucket_obj = client.get_bucket(bucket)
        blobs = bucket_obj.list_blobs(prefix=prefix)
        return sum(b.size for b in blobs)

    def list_dir(self, path: str) -> list[str]:
        if not path.startswith("gs://"):
            raise ValueError("path must be a GCS object")
        if not path.endswith("/"):
            path += "/"
        client = gcs.Client()
        remote_path = path[len("gs://") :]
        bucket_name, *rest = remote_path.split("/")
        prefix = "/".join(rest)
        bucket = client.get_bucket(bucket_name)
        # Get the objects under the 'source' path
        blobs = bucket.list_blobs(prefix=prefix)
        return [f"gs://{blob.bucket.name}/{blob.name}" for blob in blobs]

    def download_recursive(self, source: str, destination: str) -> None:
        if not source.startswith("gs://"):
            raise ValueError("source must be a GCS object")
        if not source.endswith("/"):
            source += "/"
        client = gcs.Client()
        remote_path = source[len("gs://") :]
        parts = remote_path.split("/")
        bucket_name = parts[0]
        bucket = client.bucket(bucket_name)
        source_blob_name = "/".join(parts[1:])
        bucket = client.get_bucket(bucket_name)
        # Get the objects under the 'source' path
        blobs = bucket.list_blobs(prefix=source_blob_name)
        for blob in blobs:
            if blob.name.endswith("/"):
                # Not a file
                continue
            remote_file = Path(blob.name).relative_to(source_blob_name)
            remote_directory = Path(blob.name).parent.relative_to(source_blob_name)
            local_path = Path(destination) / remote_directory
            local_path.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(Path(destination) / remote_file)

    def upload_recursive(self, source: str, destination: str) -> None:
        if not destination.startswith("gs://"):
            raise ValueError("destination must be a GCS object")
        if not destination.endswith("/"):
            destination += "/"

        source_path = Path(source)
        if not source_path.is_dir():
            raise ValueError("source must be a local directory")

        storage_client = gcs.Client()
        bucket_name, bucket_path = _split_bucket_path(destination)
        destination_bucket = storage_client.bucket(bucket_name)

        source_paths = [path for path in source_path.rglob("*") if path.is_file()]
        relative_paths = [path.relative_to(source) for path in source_paths]
        string_paths = [str(path) for path in relative_paths]

        if bucket_path != "":
            assert bucket_path[-1] == "/"  # See above
            prefix = bucket_path
        else:
            prefix = ""
        results = transfer_manager.upload_many_from_filenames(
            destination_bucket,
            string_paths,
            source_directory=source,
            blob_name_prefix=prefix,
        )

        exceptions: list[Exception] = []
        exception_names: list[str] = []
        for name, result in zip(string_paths, results):
            if isinstance(result, Exception):
                exceptions.append(result)
                exception_names.append(name)
        if exceptions:
            raise RuntimeError(f"upload failed: {exception_names}") from exceptions[0]

    def signed_url_for_dataset_upload(
        self,
        dataset_id: str,
        artifact: Artifact,
        *,
        size_limit_bytes: Optional[int] = None,
        storage_path: Optional[str] = None,
    ) -> StorageSignedURL:
        if size_limit_bytes is None:
            size_limit_bytes = max_artifact_size_bytes()
        if artifact.digest.md5 is None:
            raise ValueError("requires artifact.digest.md5")
        storage_path = storage_path or paths.dataset_root(dataset_id)
        bucket_name = _bucket_name_from_path(storage_path)
        client = gcs.Client()
        blob = client.bucket(bucket_name).blob(f"{dataset_id}/{artifact.path}")

        auth_request = google.auth.transport.requests.Request()
        signing_credentials = google.auth.compute_engine.IDTokenCredentials(
            auth_request,
            "api-server.dyff.io",
            service_account_email="api-server@dyff-354017.iam.gserviceaccount.com",
        )

        # Google custom header limiting the size of the artifact
        headers = {
            "x-goog-content-length-range": f"0,{size_limit_bytes}",
        }
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(hours=1),
            method="PUT",
            content_md5=artifact.digest.md5,
            headers=headers.copy(),  # The function mutates this argument
            credentials=signing_credentials,
        )
        return StorageSignedURL(url=url, method="PUT", headers=headers)

    def dataset_artifact_md5hash(
        self, dataset_id: str, artifact_path: str, *, storage_path: Optional[str] = None
    ) -> bytes:
        storage_path = storage_path or paths.dataset_root(dataset_id)
        bucket_name = _bucket_name_from_path(storage_path)
        client = gcs.Client()
        blob = client.bucket(bucket_name).get_blob(f"{dataset_id}/{artifact_path}")
        if blob is None:
            raise ValueError(
                f"no artifact {artifact_path} stored for dataset {dataset_id}"
            )
        return base64.b64decode(blob.md5_hash)


__all__ = ["GCloudStorageBackend"]
