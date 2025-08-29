# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import functools
import hashlib
import io
import json

# mypy: disable-error-code="import-untyped"
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Optional, Tuple
from urllib.parse import urlparse

import minio
import minio.api
import minio.helpers
import minio.time

from dyff.schema.dataset import max_artifact_size_bytes
from dyff.schema.errors import PlatformError
from dyff.schema.platform import Artifact, ArtifactURL, Entities, StorageSignedURL
from dyff.storage import paths
from dyff.storage.backend.base.storage import StorageBackend
from dyff.storage.config import config


class _MyMinio(minio.Minio):
    def presigned_url_for_base(
        self,
        base_url: str,
        method: str,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(days=7),
        response_headers: minio.helpers.DictType | None = None,
        request_date: datetime | None = None,
        version_id: str | None = None,
        extra_query_params: minio.helpers.DictType | None = None,
    ) -> str:
        """Get presigned URL of an object relative to an arbitrary base URL, for HTTP
        method, expiry time and custom request parameters.

        The base URL can contain a "netloc" and an optional scheme. If a scheme
        is provided, it must be either 'http' or 'https'.

        :param base_url: The base URL where the client will access the s3
            system. Examples: ``s3.some.domain:9000``, ``https://other.domain``.
        :param method: HTTP method.
        :param bucket_name: Name of the bucket.
        :param object_name: Object name in the bucket.
        :param expires: Expiry in seconds; defaults to 7 days.
        :param response_headers: Optional response_headers argument to
                                 specify response fields like date, size,
                                 type of file, data about server, etc.
        :param request_date: Optional request_date argument to
                             specify a different request date. Default is
                             current date.
        :param version_id: Version ID of the object.
        :param extra_query_params: Extra query parameters for advanced usage.
        :return: URL string.

        Example::
            # Get presigned URL string to PUT 'my-object' in
            # 'my-bucket' with one day expiry, where the client
            # will access the s3 system at 'https://s3.mysite.com'.
            url = client.presigned_url_for_base(
                "https://s3.mysite.com",
                "PUT",
                "my-bucket",
                "my-object",
                expires=timedelta(days=1),
            )
            print(url)
        """
        # Same as get_presigned_url(), except we modify the URL before signing

        minio.api.check_bucket_name(bucket_name, s3_check=self._base_url.is_aws_host)
        minio.api.check_non_empty_string(object_name)
        if expires.total_seconds() < 1 or expires.total_seconds() > 604800:
            raise ValueError("expires must be between 1 second to 7 days")

        region = self._get_region(bucket_name)
        query_params = extra_query_params or {}
        query_params.update({"versionId": version_id} if version_id else {})
        query_params.update(response_headers or {})
        creds = self._provider.retrieve() if self._provider else None
        if creds and creds.session_token:
            query_params["X-Amz-Security-Token"] = creds.session_token
        url = self._base_url.build(
            method,
            region,
            bucket_name=bucket_name,
            object_name=object_name,
            query_params=query_params,
        )

        # Modify the URL
        parsed_base_url = urlparse(base_url)
        if not parsed_base_url.netloc:
            parsed_base_url = urlparse(f"https://{base_url}")
        if any(
            [
                parsed_base_url.path,
                parsed_base_url.query,
                parsed_base_url.params,
                parsed_base_url.fragment,
            ]
        ):
            raise ValueError(
                f"'base_url' must be only 'scheme://netloc' ; got {base_url}"
            )
        url = minio.helpers.url_replace(
            url, scheme=parsed_base_url.scheme, netloc=parsed_base_url.netloc
        )

        if creds:
            url = minio.api.presign_v4(
                method,
                url,
                region,
                creds,
                request_date or minio.time.utcnow(),
                int(expires.total_seconds()),
            )
        return minio.api.urlunsplit(url)


def _bucket_name_from_path(path: str) -> str:
    return _split_bucket_path(path)[0]


def _drop_protocol(path: str) -> str:
    protocol = "s3://"
    if path.startswith(protocol):
        path = path[len(protocol) :]
    return path


def _split_bucket_path(path: str) -> Tuple[str, str]:
    path = _drop_protocol(path)
    parts = path.split("/")
    return parts[0], "/".join(parts[1:])


def _configured_internal_endpoint() -> str:
    if config.storage.s3.internal_endpoint is not None:
        return config.storage.s3.internal_endpoint
    else:
        return config.storage.s3.endpoint


def _get_client() -> _MyMinio:
    endpoint = _configured_internal_endpoint()
    parsed_endpoint = urlparse(endpoint, scheme="https")
    if parsed_endpoint.scheme == "http":
        secure = False
    else:
        secure = True
    parsed_endpoint = parsed_endpoint._replace(scheme="")
    return _MyMinio(
        # Minio doesn't allow paths in the URL
        endpoint=parsed_endpoint.netloc,
        access_key=config.storage.s3.access_key,
        secret_key=config.storage.s3.secret_key.get_secret_value(),
        secure=secure,
    )


def _translate_errors(fn):
    @functools.wraps(fn)
    def _impl(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except minio.S3Error as ex:
            if ex.code in ["NoSuchKey", "NoSuchBucket", "ResourceNotFound"]:
                raise KeyError(f"{ex._resource} ({ex.code})")
            raise

    return _impl


# The following function is adapted from the following project:
# https://github.com/p2p-ld/numpydantic/blob/66fffc49f87bfaaa2f4d05bf1730c343b10c9cc6/src/numpydantic/serialization.py#L107-L142
# MIT License: https://github.com/p2p-ld/numpydantic/blob/main/LICENSE
def _py312_relative_path(
    self: Path | str, other: Path | str, walk_up: bool = True
) -> Path:
    """ "Backport" of :meth:`pathlib.Path.relative_to` with ``walk_up=True`` that's not
    available pre 3.12.

    Return the relative path to another path identified by the passed
    arguments.  If the operation is not possible (because this is not
    related to the other path), raise ValueError.

    The *walk_up* parameter controls whether `..` may be used to resolve
    the path.

    References:
        https://github.com/python/cpython/blob/8a2baedc4bcb606da937e4e066b4b3a18961cace/Lib/pathlib/_abc.py#L244-L270
    """
    if not isinstance(self, Path):
        self = Path(self)
    if not isinstance(other, Path):
        other = Path(other)
    self_parts = self.parts
    other_parts = other.parts
    anchor0, parts0 = self_parts[0], list(reversed(self_parts[1:]))
    anchor1, parts1 = other_parts[0], list(reversed(other_parts[1:]))
    if anchor0 != anchor1:
        raise ValueError(f"{self!r} and {other!r} have different anchors")
    while parts0 and parts1 and parts0[-1] == parts1[-1]:
        parts0.pop()
        parts1.pop()
    for part in parts1:
        if not part or part == ".":
            pass
        elif not walk_up:
            raise ValueError(f"{self!r} is not in the subpath of {other!r}")
        elif part == "..":
            raise ValueError(f"'..' segment in {other!r} cannot be walked")
        else:
            parts0.append("..")
    return Path(*reversed(parts0))


class S3StorageBackend(StorageBackend):
    @_translate_errors
    def storage_size(self, path: str) -> int:
        bucket, prefix = _split_bucket_path(path)
        client = _get_client()
        objects = client.list_objects(bucket, prefix, recursive=True)
        return sum(obj.size for obj in objects)

    @_translate_errors
    def list_dir(self, path: str, *, recursive: bool = False) -> Iterable[str]:
        if not path.startswith("s3://"):
            raise ValueError("path must be an s3 object")
        if not path.endswith("/"):
            path += "/"
        client = _get_client()
        remote_path = path[len("s3://") :]
        bucket_name, *rest = remote_path.split("/")
        prefix = "/".join(rest)
        objects = client.list_objects(bucket_name, prefix, recursive=recursive)
        yield from (f"s3://{obj.bucket_name}/{obj.object_name}" for obj in objects)

    @_translate_errors
    def download_recursive(self, source: str, destination: str) -> None:
        if not source.startswith("s3://"):
            raise ValueError("source must be an s3 object")
        if not source.endswith("/"):
            source += "/"
        client = _get_client()
        remote_path = source[len("s3://") :]
        bucket_name, *rest = remote_path.split("/")
        prefix = "/".join(rest)
        objects = client.list_objects(bucket_name, prefix, recursive=True)

        destination_resolved = Path(destination).resolve()

        for obj in objects:
            if obj.object_name.endswith("/"):
                # Not a file
                continue
            remote_file = Path(obj.object_name).relative_to(prefix)
            remote_directory = Path(obj.object_name).parent.relative_to(prefix)
            local_directory = destination_resolved / remote_directory
            local_directory.mkdir(parents=True, exist_ok=True)
            local_file = destination_resolved / remote_file
            client.fget_object(obj.bucket_name, obj.object_name, str(local_file))

        def require_tree_contains_child(tree: Path, child: Path) -> None:
            try:
                (tree / child).resolve().relative_to(tree)
            except ValueError as ex:
                raise ValueError(f"{child} is not a descendent of {tree}") from ex

        # Restore symlinks, if present
        # Note that this only looks for the symlinks.json file in the root
        # directory; it's meant to restore a matching call to upload_recursive()
        try:
            with open(destination_resolved / ".dyff" / "symlinks.json", "r") as fin:
                symlinks: list[dict[str, Any]] = json.load(fin)["symlinks"]
        except FileNotFoundError:
            pass
        else:
            print(f"restoring symlinks:\n{json.dumps(symlinks, indent=4)}")
            for entry in symlinks:
                link = destination_resolved / str(entry["link"])
                require_tree_contains_child(destination_resolved, link)
                target = Path(entry["target"])
                target_is_directory = bool(entry["target_is_directory"])
                if target.is_absolute():
                    # Not allowed because things will break if an absolute path
                    # is restored with a different prefix.
                    raise ValueError(
                        f"absolute symlink targets are not allowed: {target}"
                    )
                # The link target is relative to the link file
                # Note: This will follow links-to-links. It will not catch the
                # case where a link points outside the tree, but it points to
                # another link that points back inside the tree.
                require_tree_contains_child(destination_resolved, link / target)
                print(f"link: {link} -> {target}")
                link.parent.mkdir(exist_ok=True, parents=True)
                link.symlink_to(target, target_is_directory=target_is_directory)

    @_translate_errors
    def upload_recursive(self, source: str, destination: str) -> None:
        if not destination.startswith("s3://"):
            raise ValueError("destination must be an s3 object")
        if not destination.endswith("/"):
            destination += "/"

        source_path = Path(source).resolve()
        if not source_path.is_dir():
            raise ValueError("source must be a local directory")

        client = _get_client()
        bucket_name, bucket_path = _split_bucket_path(destination)

        # We need to record symlink info out-of-band because s3 has no concept
        # of symlinks and it will upload the target file instead
        source_paths: list[Path] = []
        symlinks: list[dict[str, Any]] = []
        for path in source_path.rglob("*"):
            if path.is_file():
                if path.is_symlink():
                    target = path.readlink()
                    if target.is_absolute():
                        # The target has to be relative to the link file or
                        # restoration will fail if the path prefix is different
                        target = _py312_relative_path(target, path.parent, walk_up=True)
                    symlinks.append(
                        {
                            "link": str(path.relative_to(source_path)),
                            "target": str(target),
                            "target_is_directory": target.is_dir(),
                        }
                    )
                else:
                    source_paths.append(path)
        relative_paths = [path.relative_to(source) for path in source_paths]

        if bucket_path != "":
            assert bucket_path[-1] == "/"  # See above
            prefix = bucket_path
        else:
            prefix = ""

        for file_path, upload_location in zip(source_paths, relative_paths):
            client.fput_object(
                bucket_name, f"{prefix}{upload_location}", str(file_path)
            )
        if symlinks:
            data = json.dumps({"symlinks": symlinks}).encode()
            client.put_object(
                bucket_name,
                f"{prefix}.dyff/symlinks.json",
                io.BytesIO(data),
                len(data),
            )

    @_translate_errors
    def put_object(self, data: bytes | BinaryIO, destination: str) -> None:
        if not destination.startswith("s3://"):
            raise ValueError("destination must be an s3 object")
        bucket_name, bucket_path = _split_bucket_path(destination)
        if bucket_path.endswith("/"):
            raise ValueError("destination is a directory")
        if isinstance(data, bytes):
            data = io.BytesIO(data)
        _get_client().put_object(
            bucket_name, bucket_path, data, length=-1, part_size=10 * 1024 * 1024
        )

    @_translate_errors
    def get_object(self, source: str) -> BinaryIO:
        if not source.startswith("s3://"):
            raise ValueError("source must be an s3 object")
        bucket_name, bucket_path = _split_bucket_path(source)
        if bucket_path.endswith("/"):
            raise ValueError("source is a directory")

        try:
            response = _get_client().get_object(bucket_name, bucket_path)
            return io.BytesIO(response.data)
        finally:
            response.close()
            response.release_conn()

    @_translate_errors
    def delete_object(self, destination: str) -> None:
        if not destination.startswith("s3://"):
            raise ValueError("destination must be an s3 object")
        bucket_name, bucket_path = _split_bucket_path(destination)
        if bucket_path.endswith("/"):
            raise ValueError("destination is a directory")

        _get_client().remove_object(bucket_name, bucket_path)

    @_translate_errors
    def delete_tree(self, destination: str) -> None:
        if not destination.startswith("s3://"):
            raise ValueError("destination must be an s3 object")
        bucket_name, bucket_path = _split_bucket_path(destination)
        if bucket_path.endswith("/"):
            raise ValueError("destination is a directory")

        # From code example here:
        # https://min.io/docs/minio/linux/developers/python/API.html#remove-objects-bucket-name-delete-object-list-bypass-governance-mode-false
        client = _get_client()
        to_delete = [
            minio.api.DeleteObject(obj.object_name)
            for obj in client.list_objects(bucket_name, bucket_path, recursive=True)
        ]
        errors = client.remove_objects(bucket_name, to_delete)
        if errors:
            raise PlatformError(f"Failed to remove objects: {errors}")

    @_translate_errors
    def signed_url_for_artifact_upload(
        self,
        artifact: Artifact,
        storage_path: str,
        *,
        size_limit_bytes: Optional[int] = None,
        _internal_client: bool = False,
    ) -> StorageSignedURL:
        """Create a temporary signed URL that can be used in a PUT request to upload an
        ``Artifact`` directly to storage."""
        if size_limit_bytes is None:
            size_limit_bytes = max_artifact_size_bytes()
        if artifact.digest.md5 is None:
            raise ValueError("requires artifact.digest.md5")
        bucket_name, bucket_path = _split_bucket_path(storage_path)
        client = _get_client()

        # If the s3 provider is self-hosted (e.g. Minio), external clients
        # connect to it at a different URL than internal clients. We must sign
        # the correct URL, depending on which kind of client will use it.
        if _internal_client and config.storage.s3.internal_endpoint is not None:
            configured_url = config.storage.s3.internal_endpoint
        else:
            configured_url = config.storage.s3.endpoint

        signed_url = client.presigned_url_for_base(
            configured_url,
            "PUT",
            bucket_name,
            f"{bucket_path}/{artifact.path}",
            expires=timedelta(hours=1),
        )

        headers: dict[str, str] = {
            # TODO: Is there an s3 equivalent of this?
            # Google custom header limiting the size of the artifact
            # "x-goog-content-length-range": f"0,{size_limit_bytes}",
        }
        return StorageSignedURL(url=signed_url, method="PUT", headers=headers)

    @_translate_errors
    def signed_url_for_dataset_upload(
        self,
        dataset_id: str,
        artifact: Artifact,
        *,
        size_limit_bytes: Optional[int] = None,
        storage_path: Optional[str] = None,
        _internal_client: bool = False,
    ) -> StorageSignedURL:
        storage_path = storage_path or paths.dataset_root(dataset_id)
        return self.signed_url_for_artifact_upload(
            artifact,
            storage_path,
            size_limit_bytes=size_limit_bytes,
            _internal_client=_internal_client,
        )

    def _artifact_url_for_downlink(
        self,
        *,
        root_path: str,
        artifact_path: str,
        client: _MyMinio | None = None,
        _internal_client: bool = False,
    ) -> ArtifactURL:
        bucket_name, bucket_path = _split_bucket_path(artifact_path)
        relative_path = Path(bucket_path).relative_to(root_path)
        # TODO: Populate contentType and digest
        artifact = Artifact(path=str(relative_path))

        if client is None:
            client = _get_client()

        # If the s3 provider is self-hosted (e.g. Minio), external clients
        # connect to it at a different URL than internal clients. We must sign
        # the correct URL, depending on which kind of client will use it.
        if _internal_client and config.storage.s3.internal_endpoint is not None:
            configured_url = config.storage.s3.internal_endpoint
        else:
            configured_url = config.storage.s3.endpoint

        signed_url = client.presigned_url_for_base(
            configured_url,
            "GET",
            bucket_name,
            bucket_path,
            expires=timedelta(hours=1),
        )

        headers: dict[str, str] = {}
        return ArtifactURL(
            artifact=artifact,
            signedURL=StorageSignedURL(url=signed_url, method="GET", headers=headers),
        )

    @_translate_errors
    def logs_downlink(
        self, entity_kind: Entities, entity_id: str, *, _internal_client: bool = False
    ) -> Optional[ArtifactURL]:
        if entity_kind not in [
            Entities.Measurement,
            Entities.Report,
            Entities.SafetyCase,
        ]:
            return None

        storage_root = paths.entity_artifacts_root(entity_kind, entity_id)
        _root_bucket, root_path = _split_bucket_path(storage_root)
        artifact_path = paths.logs_file_for_entity(storage_root)
        return self._artifact_url_for_downlink(
            root_path=root_path,
            artifact_path=artifact_path,
            _internal_client=_internal_client,
        )

    @_translate_errors
    def artifact_downlinks(
        self, entity_kind: Entities, entity_id: str, *, _internal_client: bool = False
    ) -> Iterable[ArtifactURL]:
        storage_root = paths.entity_artifacts_root(entity_kind, entity_id)
        _root_bucket, root_path = _split_bucket_path(storage_root)
        artifact_paths = self.list_dir(storage_root, recursive=True)
        client = _get_client()

        for artifact_path in artifact_paths:
            yield self._artifact_url_for_downlink(
                root_path=root_path,
                artifact_path=artifact_path,
                client=client,
                _internal_client=_internal_client,
            )

    @_translate_errors
    def object_md5hash(self, storage_path: str) -> bytes:
        bucket_name, bucket_path = _split_bucket_path(storage_path)
        client = _get_client()

        response = None
        try:
            response = client.get_object(bucket_name, bucket_path)
            if response is None:
                raise ValueError(f"no object {storage_path}")
            # FIXME: This is potentially a very expensive operation. We have to
            # compute it on the server for security, but we should cache it in
            # the object metadata if we can confirm that users can't alter the
            # metadata using the signed upload URLs.
            # Also consider the s3 mechanisms for pre-computing digests as
            # metadata (but note that it doesn't support md5):
            # https://aws.amazon.com/blogs/aws/new-additional-checksum-algorithms-for-amazon-s3/
            return hashlib.md5(response.read()).digest()
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    @_translate_errors
    def dataset_artifact_md5hash(
        self, dataset_id: str, artifact_path: str, *, storage_path: Optional[str] = None
    ) -> bytes:
        storage_path = storage_path or paths.dataset_root(dataset_id)
        return self.object_md5hash(f"{storage_path}/{dataset_id}/{artifact_path}")


__all__ = ["S3StorageBackend"]
