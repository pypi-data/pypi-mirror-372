# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from dyff.schema.platform import Entities
from dyff.storage.config import config


def auditprocedure_notebook(auditprocedure_id: str) -> str:
    return f"{config.resources.auditprocedures.storage.url}/{auditprocedure_id}/notebook.ipynb"


def auditreport_html(audit_id: str) -> str:
    return f"{auditreport_root(audit_id)}/index.html"


def auditreport_root(audit_id: str) -> str:
    return f"{config.resources.auditreports.storage.url}/{audit_id}"


def dataset_root(dataset_id: str) -> str:
    return f"{config.resources.datasets.storage.url}/{dataset_id}"


def dataset_data(dataset_id: str) -> str:
    return f"{dataset_root(dataset_id)}/data"


def dataset_strata(dataset_id: str) -> str:
    # FIXME: Handle multi-file data (or choose a better name than 'part-0')
    return f"{dataset_root(dataset_id)}/strata/part-0.parquet"


def dataset_task(dataset_id: str, task_id: str) -> str:
    return f"{config.resources.datasets.storage.url}/{dataset_id}/tasks/{task_id}"


def datasource_root(datasource_id: str) -> str:
    return f"{config.resources.datasources.storage.url}/{datasource_id}"


def measurements_root(measurement_id: str) -> str:
    return f"{config.resources.measurements.storage.url}/{measurement_id}"


def module_root(module_id: str) -> str:
    return f"{config.resources.modules.storage.url}/{module_id}"


def outputs_raw(evaluation_id: str) -> str:
    return f"{config.resources.outputs.storage.url}/{evaluation_id}/data"


def outputs_verified(evaluation_id: str) -> str:
    return f"{config.resources.outputs.storage.url}/{evaluation_id}/verified"


def report_data(report_id: str) -> str:
    # FIXME: Handle multi-file data (or choose a better name than 'part-0')
    return f"{report_root(report_id)}/part-0.parquet"


def report_root(report_id: str) -> str:
    return f"{config.resources.reports.storage.url}/{report_id}"


def safetycase_root(safetycase_id: str) -> str:
    return f"{config.resources.safetycases.storage.url}/{safetycase_id}"


def inferenceservice_source_archive(inferenceservice_id: str) -> str:
    return f"{config.resources.inferenceservices.storage.url}/{inferenceservice_id}/source.tar.gz"


def model_source_archive(model_id: str) -> str:
    return f"{config.resources.models.storage.url}/{model_id}/source.tar.gz"


def logs_file_for_entity(entity_root: str) -> str:
    return f"{entity_root}/.dyff/logs.txt"


def entity_artifacts_root(kind: Entities, id: str) -> str:
    if kind == Entities.Dataset:
        return dataset_root(id)
    elif kind == Entities.Evaluation:
        return outputs_verified(id)
    elif kind == Entities.Measurement:
        return measurements_root(id)
    elif kind == Entities.Module:
        return module_root(id)
    elif kind == Entities.Report:
        return report_root(id)
    elif kind == Entities.SafetyCase:
        return safetycase_root(id)
    else:
        raise ValueError(f"entity kind {kind} has no associated artifacts")
