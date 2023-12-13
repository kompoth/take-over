"""
Data models
"""

from pydantic import (
    BaseModel,
    BeforeValidator,
    TypeAdapter,
    HttpUrl,
    Field,
    model_validator,
)
from datetime import datetime, timezone
from typing import Annotated
from annotated_types import Len
from hashlib import md5


def __fix_dttm(val):
    if isinstance(val, str):
        val = datetime.fromisoformat(val)
    if val.tzinfo is None:
        val.replace(tzinfo=timezone.utc)
    return val


# Some pre-annotated types
_DTTM_Meta = Annotated[datetime, BeforeValidator(__fix_dttm)]
_SHA_Meta = Annotated[str, Len(40, 40)]
_UUID_Meta = Annotated[str, Len(24, 32), BeforeValidator(lambda x: str(x))]
_URL_Meta = Annotated[
    str,
    BeforeValidator(lambda x: str(TypeAdapter(HttpUrl).validate_python(x))),
]


# Parent object for all database entities. Basically just adds uuid.
class _MongoEntity(BaseModel, validate_assignment=True):
    uuid: _UUID_Meta | None = Field(default=None, alias="_id")

    class Config:
        populate_by_name = True


class NewUser(BaseModel):
    name: str
    password: str
    email: str | None = None


class NewProject(BaseModel):
    name: str
    url: _URL_Meta


class NewJob(BaseModel):
    project_id: _UUID_Meta
    branch: str
    commit_sha: _SHA_Meta
    commit_dttm: _DTTM_Meta
    job_name: str
    coverage_value: float


class User(NewUser, _MongoEntity):
    @model_validator(mode="before")
    def autofill_uuid(cls, vals):
        if "uuid" not in vals:
            src_str = str(vals["name"])
            vals["uuid"] = md5(src_str.encode("utf-8")).hexdigest()
        return vals


class Project(NewProject, _MongoEntity):
    @model_validator(mode="before")
    def autofill_uuid(cls, vals):
        if "uuid" not in vals:
            src_str = str(vals["name"]) + str(vals["url"])
            vals["uuid"] = md5(src_str.encode("utf-8")).hexdigest()
        return vals


class Commit(_MongoEntity):
    project_id: _UUID_Meta
    branch: str
    sha: _SHA_Meta
    dttm: _DTTM_Meta

    @model_validator(mode="before")
    def autofill_uuid(cls, vals):
        if "uuid" not in vals:
            src_str = str(vals["project_id"]) + str(vals["sha"])
            vals["uuid"] = md5(src_str.encode("utf-8")).hexdigest()
        return vals


class Report(_MongoEntity):
    commit_id: _UUID_Meta
    branch: str
    job_name: str
    coverage_value: float

    @model_validator(mode="before")
    def autofill_uuid(cls, vals):
        if "uuid" not in vals:
            src_str = str(vals["commit_id"]) + str(vals["job_name"])
            vals["uuid"] = md5(src_str.encode("utf-8")).hexdigest()
        return vals


class UserXProject(_MongoEntity):
    user_id: _UUID_Meta
    project_id: _UUID_Meta

    @model_validator(mode="before")
    def autofill_uuid(cls, vals):
        if "uuid" not in vals:
            src_str = str(vals["user_id"]) + str(vals["project_id"])
            vals["uuid"] = md5(src_str.encode("utf-8")).hexdigest()
        return vals
