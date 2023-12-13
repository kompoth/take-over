"""
API router to load coverage reports
"""

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pymongo.errors import DuplicateKeyError

from app.models import NewJob, Report, Commit
from app.db import db, NotFoundError

router = APIRouter(prefix="/job", tags=["Jobs"])


@router.post("/")
def post_job(job: NewJob) -> Report:
    # Find corresponding commit; create, if there is no one
    commit = Commit(
        project_id=job.project_id,
        branch=job.branch,
        sha=job.commit_sha,
        dttm=job.commit_dttm,
    )
    found = db.get_commit(commit.uuid)
    if not found:
        try:
            db.save_commit(commit)
        except NotFoundError as ex:
            raise HTTPException(status_code=404, detail=str(ex))

    # Save report
    rr = Report(
        commit_id=commit.uuid,
        branch=commit.branch,
        job_name=job.job_name,
        coverage_value=job.coverage_value,
    )
    try:
        return db.save_report(rr)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409, detail=f"Report already exists: {rr.uuid}"
        )
