"""
API router to work with Projects
"""

from typing import Annotated
from fastapi import APIRouter, Path, Query
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

from app.models import Project
from app.db import db
from app.utils.badge import get_badge_url

router = APIRouter(prefix="/project", tags=["Projects"])


# @router.get("")
# def get_projects(
# ) -> List[Project]:
#     return db.list_projects()


@router.get("/{project_id}")
def get_project(
    project_id: Annotated[str, Path(description="Project ID")],
) -> Project:
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=404, detail=f"Project doesn't exist: {project_id}"
        )
    return project


@router.get("/{project_id}/badge.svg")
def get_badge(
    project_id: Annotated[str, Path(description="Project ID")],
    branch: Annotated[str | None, Query(description="Branch name")] = None,
) -> RedirectResponse:
    commit = db.get_last_commit(project_id, branch)
    rrs = db.get_reports(commit.uuid)
    coverage = min(x.coverage_value for x in rrs)
    return RedirectResponse(get_badge_url(coverage))
