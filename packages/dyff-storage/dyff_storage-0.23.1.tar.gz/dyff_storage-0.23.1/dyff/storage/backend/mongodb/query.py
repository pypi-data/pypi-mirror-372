# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Collection, Iterable, Optional, TypeVar

import pymongo

from dyff.schema.errors import ClientError
from dyff.schema.platform import (
    Audit,
    Dataset,
    DataSource,
    Documentation,
    DyffEntity,
    Entities,
    Evaluation,
    Family,
    InferenceService,
    InferenceSession,
    Labeled,
    Measurement,
    Method,
    Model,
    Module,
    Report,
    Resources,
    SafetyCase,
    Score,
    UseCase,
)
from dyff.schema.requests import (
    AuditQueryRequest,
    DatasetQueryRequest,
    DocumentationEditRequest,
    DocumentationQueryRequest,
    EvaluationQueryRequest,
    FamilyQueryRequest,
    InferenceServiceQueryRequest,
    InferenceSessionQueryRequest,
    MeasurementQueryRequest,
    MethodQueryRequest,
    ModelQueryRequest,
    ModuleQueryRequest,
    ReportQueryRequest,
    SafetyCaseQueryRequest,
    ScoreQueryRequest,
    UseCaseQueryRequest,
)
from dyff.storage.backend.base.query import QueryBackend, Whitelist
from dyff.storage.config import config

_DyffEntityT = TypeVar("_DyffEntityT", bound=DyffEntity)


class MongoDBQueryBackend(QueryBackend):
    # Mapping of query keys in the API to the corresponding DB fields
    query_key_map = {
        Entities.Evaluation: {
            "inferenceService": "inferenceSession.inferenceService.id",
            "inferenceServiceName": "inferenceSession.inferenceService.name",
            "model": "inferenceSession.inferenceService.model.id",
            "modelName": "inferenceSession.inferenceService.model.name",
        },
        Entities.InferenceService: {
            "model": "model.id",
            "modelName": "model.name",
        },
        Entities.InferenceSession: {
            "inferenceService": "inferenceService.id",
            "inferenceServiceName": "inferenceService.name",
            "model": "inferenceService.model.id",
            "modelName": "inferenceService.model.name",
        },
        Entities.Measurement: {
            "method": "method.id",
            "methodName": "method.name",
            "dataset": "scope.dataset",
            "evaluation": "scope.evaluation",
            "inferenceService": "scope.inferenceService",
            "model": "scope.model",
        },
        Entities.Method: {
            "outputKind": "output.kind",
        },
        Entities.SafetyCase: {
            "method": "method.id",
            "methodName": "method.name",
            "dataset": "scope.dataset",
            "evaluation": "scope.evaluation",
            "inferenceService": "scope.inferenceService",
            "model": "scope.model",
        },
        Entities.Score: {
            "method": "metadata.refs.method",
            "dataset": "metadata.refs.dataset",
            "evaluation": "metadata.refs.evaluation",
            "inferenceService": "metadata.refs.inferenceService",
            "model": "metadata.refs.model",
        },
    }

    def __init__(self):
        connection_string = config.api.query.mongodb.connection_string
        self._client = pymongo.MongoClient(connection_string.get_secret_value())
        self._workflows_db = self._client.get_database(
            config.api.query.mongodb.database
        )

    def _convert_entity_response(self, kind: Entities, entity: dict) -> dict:
        def array_to_object(xs: list[dict]) -> dict:
            return {x["key"]: x["value"] for x in xs}

        if kind == Entities.Documentation:
            entity = dict(entity)
            entity["entity"] = entity["_id"]
            del entity["_id"]
            return entity
        else:
            entity = dict(entity)
            entity["id"] = entity["_id"]

            # dicts with user-supplied keys are stored as [(k, v)] lists
            # and need to be converted back
            if (labels := entity.get("labels")) is not None:
                entity["labels"] = array_to_object(labels)
            # if (annotations := entity.get("annotations")) is not None:
            #     entity["annotations"] = array_to_object(annotations)
            if kind == Entities.Family:
                if (members := entity.get("members")) is not None:
                    entity["members"] = array_to_object(members)

            del entity["_id"]
            return entity

    def _filter_from_whitelist(self, whitelist: Whitelist) -> Optional[dict]:
        if ("*" not in whitelist.accounts) and ("*" not in whitelist.entities):
            # Query constraint requiring the result to be in the whitelist
            return {
                "$or": [
                    {"account": {"$in": list(whitelist.accounts)}},
                    {"_id": {"$in": list(whitelist.entities)}},
                ]
            }
        else:
            return None

    def _get_entity(self, kind: Entities, id: str) -> Optional[dict]:
        collection_name = Resources.for_kind(kind)
        collection = self._workflows_db[collection_name]
        result = collection.find_one({"_id": id})
        if result:
            result = self._convert_entity_response(kind, result)
        return result

    def _query_entities(
        self, kind: Entities, whitelist: Whitelist, query: dict
    ) -> Iterable[dict]:
        print(f"whitelist: {whitelist}")
        mongo_conjunction: list[dict] = []
        if whitelist_filter := self._filter_from_whitelist(whitelist):
            mongo_conjunction.append(whitelist_filter)

        def json_decode(k: str, v: str):
            try:
                return json.loads(v)
            except json.decoder.JSONDecodeError:
                raise ClientError(f"{k}: json decode failed")

        def build_query(query: dict, key_map: dict[str, str]) -> list:
            conjunction: list = []
            for k, v in query.items():
                if v is None:
                    continue

                if k == "id":
                    k = "_id"
                else:
                    # Map query key to DB key, if mapping exists
                    k = key_map.get(k, k)

                if k == "labels":
                    if isinstance(v, dict):
                        labels = v
                    else:
                        labels = json_decode(k, v)
                    labeled = Labeled(labels=labels)  # validate
                    for label_key, label_value in labeled.labels.items():
                        conjunction.append(
                            {
                                k: {
                                    "$elemMatch": {
                                        "key": label_key,
                                        "value": label_value,
                                    }
                                }
                            }
                        )
                # TODO:
                # elif k == "annotations":
                #     pass
                elif k == "inputs":
                    # This is a special query for Analysis-related entities. It
                    # selects entities that reference any of the listed IDs in
                    # their .inputs field.
                    if isinstance(v, list):
                        entity_list = v
                    elif isinstance(v, str):
                        entity_list = v.split(",")
                    else:
                        raise ClientError(f"inputs: must be list or str; got {type(v)}")
                    conjunction.append(
                        {"inputs": {"$elemMatch": {"entity": {"$in": entity_list}}}}
                    )
                elif isinstance(v, list):
                    conjunction.append({k: {"$in": list(v)}})
                else:
                    conjunction.append({k: v})
            return conjunction

        key_map = MongoDBQueryBackend.query_key_map.get(kind, {})

        # These are options to the query operation and need to be removed
        # from the actual query
        options = {}
        if orderBy := query.pop("orderBy", None):
            order = query.pop("order", None)
            options["sort"] = {
                orderBy: (
                    pymongo.DESCENDING if order == "descending" else pymongo.ASCENDING
                ),
            }
        if limit := query.pop("limit", None):
            options["limit"] = limit

        json_query_string = query.pop("query", None)
        if json_query_string is not None:
            json_query_object = json_decode("query", json_query_string)
            if isinstance(json_query_object, list):
                for item in json_query_object:
                    mongo_conjunction.extend(build_query(item, key_map))
            elif isinstance(json_query_object, dict):
                mongo_conjunction.extend(build_query(json_query_object, key_map))
            else:
                raise ClientError(
                    f"query: must parse as dict or list[dict]; got {type(json_query_object)}"
                )

        mongo_conjunction.extend(build_query(query, key_map))

        mongo_query = {"$and": mongo_conjunction} if mongo_conjunction else {}
        print(f"query: {mongo_query}")
        collection_name = Resources.for_kind(kind)
        collection = self._workflows_db[collection_name]

        results = collection.find(mongo_query, **options)

        for result in results:
            yield self._convert_entity_response(kind, result)

    def expired_entities(
        self, entity_type: type[_DyffEntityT], *, before: datetime
    ) -> list[_DyffEntityT]:
        before = before.astimezone(timezone.utc)
        kind = Entities(entity_type.__name__)
        collection_name = Resources.for_kind(kind)
        collection = self._workflows_db[collection_name]
        query = {
            "status": "Deleted",
            "lastTransitionTime": {"$ne": None, "$lt": before.isoformat()},
        }
        results = collection.find(query)
        return [
            entity_type.parse_obj(self._convert_entity_response(kind, result))
            for result in results
        ]

    # ------------------------------------------------------------------------

    def get_documentation(self, resource_id: str) -> Optional[Documentation]:
        """Retrieve the Documentation entity associated with a resource.

        :param resource_id: ID of the documented resource.
        :returns: The Documentation, or None if no resource exists with the given ID.
        """
        result = self._get_entity(Entities.Documentation, resource_id)
        return Documentation.parse_obj(result) if result else None

    def query_documentation(
        self, whitelist: Whitelist, query: DocumentationQueryRequest
    ) -> Collection[Documentation]:
        """Retrieve all Documentation entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: The query request.
        """
        results = self._query_entities(Entities.Documentation, whitelist, query.dict())
        return [Documentation.parse_obj(result) for result in results]

    def get_audit(self, id: str) -> Optional[Audit]:
        """Retrieve an Audit entity.

        :param id: The unique key of the Audit.
        :returns: The Audit, or None if no Audit with the specified key exists.
        """
        result = self._get_entity(Entities.Audit, id)
        return Audit.parse_obj(result) if result else None

    def query_audits(
        self, whitelist: Whitelist, query: AuditQueryRequest
    ) -> Collection[Audit]:
        """Retrieve all Audit entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Audit entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Audit, whitelist, query.dict())
        return [Audit.parse_obj(result) for result in results]

    def get_data_source(self, id: str) -> Optional[DataSource]:
        """Retrieve a DataSource entity.

        :param id: The unique key of the DataSource.
        :returns: The DataSource, or None if no DataSource with the specified key
            exists.
        """
        result = self._get_entity(Entities.DataSource, id)
        return DataSource.parse_obj(result) if result else None

    def query_data_sources(
        self, whitelist: Whitelist, **query
    ) -> Collection[DataSource]:
        """Retrieve all DataSource entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the DataSource entity. The
            returned entities satisfy 'entity.field==value' for all items 'field: value'
            in kwargs.
        """
        results = self._query_entities(Entities.DataSource, whitelist, query)
        return [DataSource.parse_obj(result) for result in results]

    def get_dataset(self, id: str) -> Optional[Dataset]:
        """Retrieve a Dataset entity.

        :param id: The unique key of the Dataset.
        :returns: The Dataset, or None if no Dataset with the specified key exists.
        """
        result = self._get_entity(Entities.Dataset, id)
        return Dataset.parse_obj(result) if result else None

    def query_datasets(
        self, whitelist: Whitelist, query: DatasetQueryRequest
    ) -> Collection[Dataset]:
        """Retrieve all Dataset entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Dataset entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Dataset, whitelist, query.dict())
        return [Dataset.parse_obj(result) for result in results]

    def get_evaluation(self, id: str) -> Optional[Evaluation]:
        """Retrieve an Evaluation entity.

        :param id: The unique key of the Evaluation.
        :returns: The Evaluation, or None if no Evaluation with the specified key
            exists.
        """
        result = self._get_entity(Entities.Evaluation, id)
        return Evaluation.parse_obj(result) if result else None

    def query_evaluations(
        self, whitelist: Whitelist, query: EvaluationQueryRequest
    ) -> Collection[Evaluation]:
        """Retrieve all Evaluation entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Evaluation entity. The
            returned entities satisfy 'entity.field==value' for all items 'field: value'
            in kwargs.
        """
        results = self._query_entities(Entities.Evaluation, whitelist, query.dict())
        return [Evaluation.parse_obj(result) for result in results]

    def get_family(self, id: str) -> Optional[Family]:
        """Retrieve a Family entity.

        :param id: The unique ID of the Family.
        :returns: The Family, or None if no Family with the specified ID exists.
        """
        result = self._get_entity(Entities.Family, id)
        return Family.parse_obj(result) if result else None

    def query_families(
        self, whitelist: Whitelist, query: FamilyQueryRequest
    ) -> Collection[Family]:
        """Retrieve all Family entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Family entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Family, whitelist, query.dict())
        return [Family.parse_obj(result) for result in results]

    def get_inference_service(self, id: str) -> Optional[InferenceService]:
        """Retrieve an InferenceService entity.

        :param id: The unique key of the InferenceService.
        :returns: The InferenceService, or None if no InferenceService with the
            specified key exists.
        """
        result = self._get_entity(Entities.InferenceService, id)
        return InferenceService.parse_obj(result) if result else None

    def query_inference_services(
        self, whitelist: Whitelist, query: InferenceServiceQueryRequest
    ) -> Collection[InferenceService]:
        """Retrieve all InferenceService entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the InferenceService entity. The
            returned entities satisfy 'entity.field==value' for all items 'field: value'
            in kwargs.
        """
        results = self._query_entities(
            Entities.InferenceService, whitelist, query.dict()
        )
        return [InferenceService.parse_obj(result) for result in results]

    def get_inference_session(self, id: str) -> Optional[InferenceSession]:
        """Retrieve an InferenceSession entity.

        :param id: The unique key of the InferenceSession.
        :returns: The InferenceSession, or None if no InferenceSession with the
            specified key exists.
        """
        result = self._get_entity(Entities.InferenceSession, id)
        return InferenceSession.parse_obj(result) if result else None

    def query_inference_sessions(
        self, whitelist: Whitelist, query: InferenceSessionQueryRequest
    ) -> Collection[InferenceSession]:
        """Retrieve all InferenceSession entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the InferenceSession entity. The
            returned entities satisfy 'entity.field==value' for all items 'field: value'
            in kwargs.
        """
        results = self._query_entities(
            Entities.InferenceSession, whitelist, query.dict()
        )
        return [InferenceSession.parse_obj(result) for result in results]

    def get_measurement(self, id: str) -> Optional[Measurement]:
        """Retrieve a Measurement entity.

        :param id: The unique key of the Measurement.
        :returns: The Measurement, or None if no Measurement with the specified key
            exists.
        """
        result = self._get_entity(Entities.Measurement, id)
        return Measurement.parse_obj(result) if result else None

    def query_measurements(
        self, whitelist: Whitelist, query: MeasurementQueryRequest
    ) -> Collection[Measurement]:
        """Retrieve all Measurement entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Measurement entity. The
            returned entities satisfy 'entity.field==value' for all items 'field: value'
            in kwargs.
        """
        results = self._query_entities(Entities.Measurement, whitelist, query.dict())
        return [Measurement.parse_obj(result) for result in results]

    def get_method(self, id: str) -> Optional[Method]:
        """Retrieve a Method entity.

        :param id: The unique key of the Method.
        :returns: The Method, or None if no Method with the specified key exists.
        """
        result = self._get_entity(Entities.Method, id)
        return Method.parse_obj(result) if result else None

    def query_methods(
        self, whitelist: Whitelist, query: MethodQueryRequest
    ) -> Collection[Method]:
        """Retrieve all Method entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Method entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Method, whitelist, query.dict())
        return [Method.parse_obj(result) for result in results]

    def get_model(self, id: str) -> Optional[Model]:
        """Retrieve a Model entity.

        :param id: The unique key of the Model.
        :returns: The Model, or None if no Model with the specified key exists.
        """
        result = self._get_entity(Entities.Model, id)
        return Model.parse_obj(result) if result else None

    def query_models(
        self, whitelist: Whitelist, query: ModelQueryRequest
    ) -> Collection[Model]:
        """Retrieve all Model entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Model entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Model, whitelist, query.dict())
        return [Model.parse_obj(result) for result in results]

    def get_module(self, id: str) -> Optional[Module]:
        """Retrieve a Module entity.

        :param id: The unique key of the Module.
        :returns: The Module, or None if no Module with the specified key exists.
        """
        result = self._get_entity(Entities.Module, id)
        return Module.parse_obj(result) if result else None

    def query_modules(
        self, whitelist: Whitelist, query: ModuleQueryRequest
    ) -> Collection[Module]:
        """Retrieve all Module entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Module entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Module, whitelist, query.dict())
        return [Module.parse_obj(result) for result in results]

    def get_report(self, id: str) -> Optional[Report]:
        """Retrieve a Report entity.

        :param id: The unique key of the Report.
        :returns: The Report, or None if no Report with the specified key exists.
        """
        result = self._get_entity(Entities.Report, id)
        return Report.parse_obj(result) if result else None

    def query_reports(
        self, whitelist: Whitelist, query: ReportQueryRequest
    ) -> Collection[Report]:
        """Retrieve all Report entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Report entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Report, whitelist, query.dict())
        return [Report.parse_obj(result) for result in results]

    def get_safetycase(self, id: str) -> Optional[SafetyCase]:
        """Retrieve a SafetyCase entity.

        :param id: The unique key of the SafetyCase.
        :returns: The SafetyCase, or None if no SafetyCase with the specified key
            exists.
        """
        result = self._get_entity(Entities.SafetyCase, id)
        return SafetyCase.parse_obj(result) if result else None

    def query_safetycases(
        self, whitelist: Whitelist, query: SafetyCaseQueryRequest
    ) -> Collection[SafetyCase]:
        """Retrieve all SafetyCase entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the SafetyCase entity. The
            returned entities satisfy 'entity.field==value' for all items 'field: value'
            in kwargs.
        """
        results = self._query_entities(Entities.SafetyCase, whitelist, query.dict())
        return [SafetyCase.parse_obj(result) for result in results]

    def get_score(self, id: str) -> Optional[Score]:
        """Retrieve a Score entity.

        :param id: The unique key of the Score.
        :returns: The Score, or None if no Score with the specified key exists.
        """
        result = self._get_entity(Entities.Score, id)
        return Score.parse_obj(result) if result else None

    def query_scores(
        self, whitelist: Whitelist, query: ScoreQueryRequest
    ) -> Collection[Score]:
        """Retrieve all Score entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the Score entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.Score, whitelist, query.dict())
        return [Score.parse_obj(result) for result in results]

    def get_usecase(self, id: str) -> Optional[UseCase]:
        """Retrieve a UseCase entity.

        :param id: The unique key of the UseCase.
        :returns: The UseCase, or None if no UseCase with the specified key exists.
        """
        result = self._get_entity(Entities.UseCase, id)
        return UseCase.parse_obj(result) if result else None

    def query_usecases(
        self, whitelist: Whitelist, query: UseCaseQueryRequest
    ) -> Collection[UseCase]:
        """Retrieve all UseCase entities matching the query parameters.

        :param whitelist: The set of accounts and entities that the caller has been
            granted access to.
        :param query: Equality constraints on fields of the UseCase entity. The returned
            entities satisfy 'entity.field==value' for all items 'field: value' in
            kwargs.
        """
        results = self._query_entities(Entities.UseCase, whitelist, query.dict())
        return [UseCase.parse_obj(result) for result in results]

    # ------------------------------------------------------------------------
    # FIXME: Some of these methods don't belong on the "query" side, because
    # they mutate state. But, these "metadata" methods don't go through the
    # Kafka backend because the other backend components don't care about
    # metadata. Maybe there should be a third "metadata" backend to contain
    # these?

    def edit_documentation(
        self, id: str, edit: DocumentationEditRequest
    ) -> Optional[Documentation]:
        """Edit the Documentation entity associated with a resource.

        :param id: ID of the documented resource.
        :param edit: Edit request containing changes to make to the documentation.
        :returns: The new Documentation, or None if no resource exists with the given
            ID.
        """
        collection = self._workflows_db["documentation"]
        edit_dict = edit.documentation.dict()
        result = collection.find_one_and_update(
            {"_id": id},
            {"$set": edit_dict},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        if result is None:
            return None
        del result["_id"]
        return Documentation.parse_obj(result)
