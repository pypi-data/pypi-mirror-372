# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from typing import Literal
from dataclasses import dataclass

from datetime import datetime

from ..pipelines import Pipeline, PipelineArgs
from .._client import get_default_client


@dataclass
class PipelineRecord:
    id: str
    name: str
    description: str | None
    definition_yaml: str
    created_at: datetime
    updated_at: datetime

    def pipeline(self) -> Pipeline:
        return Pipeline._from_yaml(self.definition_yaml)

    @classmethod
    def from_json(cls, json: dict) -> "PipelineRecord":
        return cls(
            id=json["id"],
            name=json["name"],
            description=json["description"],
            definition_yaml=json["definition_yaml"],
            created_at=datetime.fromisoformat(json["created_at"]),
            updated_at=datetime.fromisoformat(json["updated_at"]),
        )


@dataclass
class PipelineJobRecord:
    id: str
    pipeline_id: str
    project_id: str
    name: str
    description: str | None
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    @classmethod
    def from_json(cls, json: dict) -> "PipelineJobRecord":
        return cls(
            id=json["id"],
            pipeline_id=json["pipeline_id"],
            project_id=json["project_id"],
            name=json["name"],
            description=json["description"],
            status=json["status"],
            created_at=datetime.fromisoformat(json["created_at"]),
            updated_at=datetime.fromisoformat(json["updated_at"]),
            started_at=datetime.fromisoformat(json["started_at"]) if json["started_at"] else None,
            completed_at=(
                datetime.fromisoformat(json["completed_at"]) if json["completed_at"] else None
            ),
        )


def create_pipeline(
    name: str, pipeline: Pipeline | str, description: str | None = None
) -> PipelineRecord:
    """
    Create a new pipeline.

    Parameters
    ----------
    name : str
        Name of the pipeline.
    pipeline : Pipeline | str
        The pipeline to create. Accepts a Pipeline object or a YAML-formatted pipeline definition.
    description : str, optional
        Description of the pipeline.
    """
    if isinstance(pipeline, Pipeline):
        definition_yaml = pipeline.to_yaml()
    else:
        definition_yaml = pipeline
    body = {
        "name": name,
        "definition_yaml": definition_yaml,
        "description": description,
    }
    res = get_default_client().http.post("/rest/v0/pipelines", body)
    return PipelineRecord.from_json(res)


def list_pipelines() -> list[PipelineRecord]:
    """
    List all pipelines.
    """
    res = get_default_client().http.get("/rest/v0/pipelines")
    return [PipelineRecord.from_json(p) for p in res]


def get_pipeline(id: str) -> PipelineRecord:
    """
    Get a pipeline by ID.

    Parameters
    ----------
    id : str
        ID of the pipeline to fetch.
    """
    res = get_default_client().http.get(f"/rest/v0/pipelines/{id}")
    return PipelineRecord.from_json(res)


def create_pipeline_job(
    pipeline_id: str, args: PipelineArgs, project_id: str, name: str, description: str | None = None
) -> PipelineJobRecord:
    """
    Create a new pipeline job.

    Parameters
    ----------
    pipeline_id : str
        ID of the pipeline to invoke.
    args : PipelineArgs
        Arguments to pass to the pipeline.
    project_id : str
        ID of the project to run the pipeline job in.
    name : str
        Name of the pipeline job.
    description : str, optional
        Description of the pipeline job.
    """

    arg_rows = [row.row_values for row in args.rows]
    body = {
        "name": name,
        "project_id": project_id,
        "argument_names": [p.name for p in args.params],
        "argument_rows": arg_rows,
    }

    res = get_default_client().http.post(f"/rest/v0/pipelines/{pipeline_id}/pipeline_jobs", body)
    return PipelineJobRecord.from_json(res)


def get_pipeline_job(id: str) -> PipelineJobRecord:
    """
    Get a pipeline job by ID.
    """
    res = get_default_client().http.get(f"/rest/v0/pipeline_jobs/{id}")
    return PipelineJobRecord.from_json(res)


def list_pipeline_jobs() -> list[PipelineJobRecord]:
    """
    List all pipeline jobs.
    """
    res = get_default_client().http.get("/rest/v0/pipeline_jobs")
    return [PipelineJobRecord.from_json(p) for p in res]
