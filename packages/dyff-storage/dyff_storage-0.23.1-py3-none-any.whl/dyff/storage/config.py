# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0
"""Configuration options for Dyff Platform components.

Our approach to configuration:

  1. Config options are specified with Pydantic models where all fields are
     optional.
  2. Config values are provided to the component through env variables.
  3. Env variables are named like ``DYFF_OPTION`` or
     ``DYFF_SUBCONFIG__OPTION``. The first value is available at
     ``config.option``, and the second is available at
     ``config.subconfig.option``. The nested config value requires creating
     a ``pydantic.BaseModel`` to hold the ``.subconfig`` options.
  4. When running the component in k8s, mount configuration values as
     environment variables. Mount only the subsets of the configuration that
     are required for the component. Both ``ConfigMap`` and ``Secret``
     resources can be mounted.
"""

import os
from typing import List, Optional

from pydantic import BaseModel, Field, SecretStr
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings


class KafkaConfigConfig(BaseModel):
    bootstrap_servers: str = Field(
        default="kafka.kafka.svc.cluster.local",
        description="The address to contact when establishing a connection to Kafka.",
        examples=[
            "kafka.kafka.svc.cluster.local",
            "kafka.kafka.svc.cluster.local:9093",
        ],
    )

    compression_type: str = "zstd"

    def get_producer_config(self, keys: Optional[List[str]] = None):
        if keys is None:
            keys = ["bootstrap.servers", "compression.type"]
        return {key: self.get_by_kafka_key(key) for key in keys}

    def get_by_kafka_key(self, key: str):
        field_name = key.replace(".", "_")
        return getattr(self, field_name)


class KafkaTopicsConfig(BaseModel):
    commands: str = None
    workflows_events: str = Field(
        default="dyff.workflows.events",
        examples=["test.workflows.events"],
    )
    workflows_state: str = Field(
        default="dyff.workflows.state",
        examples=["test.workflows.state"],
    )


class KafkaConfig(BaseModel):
    config: KafkaConfigConfig = Field(default_factory=KafkaConfigConfig)
    topics: KafkaTopicsConfig = Field(default_factory=KafkaTopicsConfig)


def mongodb_connection_string_field(default: Optional[str] = None) -> SecretStr:
    if default is None:
        default = ("mongodb://localhost:27017/&ssl=false",)
    return Field(
        description=(
            """Set the MongoDB connection string, following this pattern::

    mongodb+srv://[username:password@]host[/[defaultauthdb][?options]]

For more info, see the `MongoDB manual
<https://www.mongodb.com/docs/manual/reference/connection-string/>`_.
"""
        ),
        default=default,
        examples=[
            "mongodb+srv://USER:PASS@dyff-datastore-rs0.mongodb.svc.cluster.local/workflows?replicaSet=rs0&ssl=false&authSource=users",
        ],
    )


def mongodb_database_field(default=PydanticUndefined) -> str:
    return Field(
        description=("""Name of the MongoDB database to connect to."""),
        default=default,
        examples=[
            "accounts",
            "workflows",
        ],
    )


class GitlabConfig(BaseModel):
    audit_reader_access_token: SecretStr = None


class AccountsMongoDBConnection(BaseModel):
    connection_string: SecretStr = mongodb_connection_string_field()
    database: str = mongodb_database_field(default="accounts")


class WorkflowsMongoDBConnection(BaseModel):
    connection_string: SecretStr = mongodb_connection_string_field()
    database: str = mongodb_database_field(default="workflows")


class S3StorageConfig(BaseModel):
    endpoint: str = Field(
        description="External URL of the s3 server", default="s3.minio.dyff.local"
    )
    internal_endpoint: Optional[str] = Field(
        description="The URL of the s3 server that internal clients will use,"
        " if different from `endpoint`."
        " This is needed when using a self-hosted s3 provider like Minio"
        " running inside the Dyff cluster.",
        default=None,
    )
    access_key: Optional[str] = Field(
        description="Access key (aka user ID)", default=None
    )
    secret_key: SecretStr = Field(description="Secret key (aka password)", default=None)


class ApiAuthConfig(BaseModel):
    api_key_signing_secret: SecretStr = Field(
        description=(
            """A random string used for signing API keys. This value must be
kept secret. Such a random string may be generated with::

    head /dev/urandom | tr -dc A-Za-z0-9 | head -c 64 ; echo
"""
        ),
        default=None,
        examples=[
            "4oyoZHXu5D7wAUS0Wk7holW0LEiHN4WcM00b05t5DO5PKNiamTbQSroMyrLnef05"  # pragma: allowlist secret
        ],
    )

    backend: str = Field(default="dyff.storage.backend.mongodb.auth.MongoDBAuthBackend")
    mongodb: AccountsMongoDBConnection = Field(
        default_factory=AccountsMongoDBConnection
    )


class ApiCommandConfig(BaseModel):
    backend: str = Field(
        default="dyff.storage.backend.kafka.command.KafkaCommandBackend",
    )


class ApiQueryConfig(BaseModel):
    backend: str = Field(
        default="dyff.storage.backend.mongodb.query.MongoDBQueryBackend",
    )
    mongodb: WorkflowsMongoDBConnection = Field(
        default_factory=WorkflowsMongoDBConnection
    )


class ApiConfig(BaseModel):
    auth: ApiAuthConfig = Field(default_factory=ApiAuthConfig)
    command: ApiCommandConfig = Field(default_factory=ApiCommandConfig)
    query: ApiQueryConfig = Field(default_factory=ApiQueryConfig)


class StorageConfig(BaseModel):
    backend: str = Field(
        default="dyff.storage.backend.s3.storage.S3StorageBackend",
    )
    s3: S3StorageConfig = Field(default_factory=S3StorageConfig)

    audit_leaderboards_gitlab_project: str = "44711531"


class KubernetesConfig(BaseModel):
    workflows_namespace: str = Field(
        default="default",
    )


class StorageConfigV2(BaseModel):
    url: str = Field(
        description=(
            """File storage is provided by the smart_open_ package, and any
supported URL format may be used. Dyff is currently tested with Google Cloud
Storage and MinIO.

Additional configuration may be required. See the `smart_open documentation`__
for more information.

.. _smart_open: https://pypi.org/project/smart-open/

__ smart_open_
"""
        ),
        default="s3://dyff",
        examples=[
            "/path/to/dyff",
            "gs://dyff",
        ],
    )


class AuditProceduresConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-auditprocedures-785edd14c3c3f3c9"
        )
    )


class AuditReportsConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-auditreports-ef7dbc082d83b281"
        )
    )


class DataSourcesConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-rawdata-14a802b4b854421f"
        )
    )


class DataSetsConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-datasets-a1d118148ee7550e"
        )
    )


class InferenceServicesConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-inferenceservices-3ac808007f2667b9"
        )
    )


class MeasurementsConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-measurements-aaaabbbbccccdddd"
        )
    )


class ModelsConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-models-b10436edfc47d3c1"
        )
    )


class ModulesConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-modules-aaaabbbbccccdddd"
        )
    )


class OutputsConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-outputs-6f70a71477535211"
        )
    )


class ReportsConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-reports-c1caea9ce5861c9e"
        )
    )


class SafetyCasesConfig(BaseModel):
    storage: StorageConfigV2 = Field(
        default_factory=lambda: StorageConfigV2(
            url="gs://alignmentlabs-safetycases-aaaabbbbccccdddd"
        )
    )


class ResourcesConfig(BaseModel):
    auditprocedures: AuditProceduresConfig = Field(
        default_factory=AuditProceduresConfig
    )
    auditreports: AuditReportsConfig = Field(default_factory=AuditReportsConfig)
    datasources: DataSourcesConfig = Field(default_factory=DataSourcesConfig)
    datasets: DataSetsConfig = Field(default_factory=DataSetsConfig)
    inferenceservices: InferenceServicesConfig = Field(
        default_factory=InferenceServicesConfig
    )
    measurements: MeasurementsConfig = Field(default_factory=MeasurementsConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    outputs: OutputsConfig = Field(default_factory=OutputsConfig)
    reports: ReportsConfig = Field(default_factory=ReportsConfig)
    safetycases: SafetyCasesConfig = Field(default_factory=SafetyCasesConfig)


class DyffConfig(BaseSettings):
    api: ApiConfig = Field(default_factory=ApiConfig)
    resources: ResourcesConfig = Field(default_factory=ResourcesConfig)

    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    gitlab: GitlabConfig = Field(default_factory=GitlabConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig)

    class Config:
        env_file = os.environ.get("DYFF_DOTENV_FILE", ".env")
        # Env variables start with 'DYFF_'
        env_prefix = "dyff_"
        # Env var like 'DYFF_KAFKA__FOO' will be stored in 'kafka.foo'
        env_nested_delimiter = "__"


config = DyffConfig()
