# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Optional, TypeVar

from dyff.schema import ids
from dyff.schema.platform import (
    Audit,
    Dataset,
    DataSource,
    DyffEntity,
    EntityStatus,
    Evaluation,
    InferenceService,
    InferenceSession,
    Labeled,
    Model,
    Report,
)
from dyff.storage import timestamp

_EntityT = TypeVar("_EntityT", bound=DyffEntity)


class MockCommandBackend(abc.ABC):
    def _copy_and_add_system_fields(self, entity: _EntityT) -> _EntityT:
        entity = entity.copy()
        entity.creationTime = timestamp.now()
        entity.status = EntityStatus.created
        entity.id = ids.generate_entity_id()
        return entity

    def create_audit(self, spec: Audit) -> Audit:
        print(f"create_audit\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_data_source(self, spec: DataSource) -> DataSource:
        print(f"create_data_source\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_dataset(self, spec: Dataset) -> Dataset:
        print(f"create_dataset\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_evaluation(self, spec: Evaluation) -> Evaluation:
        print(f"create_evaluation\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_inference_service(self, spec: InferenceService) -> InferenceService:
        print(f"create_inference_service\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_inference_session(self, spec: InferenceSession) -> InferenceSession:
        print(f"create_inference_session\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_model(self, spec: Model) -> Model:
        print(f"create_model\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def create_report(self, spec: Report) -> Report:
        print(f"create_report\nspec: {spec.json(indent=2)}", flush=True)
        return self._copy_and_add_system_fields(spec)

    def update_status(
        self, id: str, *, status: str, reason: Optional[str] = None
    ) -> None:
        print(f"update_status: {id} {status} {reason}", flush=True)

    def update_labels(self, id: str, labels: Labeled) -> None:
        print(f"update_labels: {id}\n{labels.json(indent=2)}", flush=True)
