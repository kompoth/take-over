"""
API router to work with Projects
"""

from typing import Annotated, List
from fastapi import APIRouter, Path, Query
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError

from app.models import NewProject, Project
from app.db import db
from app.utils.badge import get_badge_url

router = APIRouter(prefix="/project", tags=["Projects"])


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
    # TODO: get coverage value from the last commit
    coverage = 40
    return RedirectResponse(get_badge_url(coverage))
