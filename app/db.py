"""
A singleton class to interact with MongoDB
"""

import os
from typing import List
from pymongo import MongoClient

from app.models import User, Project, Commit, Report, UserXProject
from app.utils.singleton import singleton

DB_USERNAME = os.getenv("TO_DB_USERNAME")
DB_PASSWORD = os.getenv("TO_DB_PASSWORD")
DB_URI = f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@localhost:27017"


class NotFoundError(Exception):
    pass


@singleton
class MongoDB:
    _client = None
    _db = None

    def __init__(self):
        self._client = MongoClient(DB_URI)
        self._db = self._client["take-over"]

    def save_project(self, project: Project) -> Project:
        model_dump = project.model_dump(by_alias=True)
        self._db["projects"].insert_one(model_dump)
        return project

    def get_project(self, project_id: str) -> Project | None:
        found = self._db["projects"].find_one({"_id": project_id})
        return None if not found else Project(**found)

    def list_projects(self, limit: int = 50) -> List[Project]:
        found = list(self._db["projects"].find().limit(limit))
        return map(lambda x: Project(**x), found)

    def save_commit(self, commit: Commit) -> Commit:
        project = self.get_project(commit.project_id)
        if not project:
            raise NotFoundError(f"Project doesn't exist: {commit.project_id}")
        model_dump = commit.model_dump(by_alias=True)
        self._db["commits"].insert_one(model_dump)
        return commit

    def get_commit(self, commit_id: str) -> Commit:
        found = self._db["commits"].find_one({"_id": commit_id})
        return None if not found else Commit(**found)

    def save_report(self, rr: Report) -> Report:
        model_dump = rr.model_dump(by_alias=True)
        self._db["reports"].insert_one(model_dump)
        return rr

    def get_user(self, user_id: str) -> User:
        found = self._db["users"].find_one({"_id": user_id})
        return None if not found else User(**found)

    def save_user(self, user: User) -> User:
        model_dump = user.model_dump(by_alias=True)
        self._db["users"].insert_one(model_dump)
        return user

    def delete_user(self, user_id) -> bool:
        res = self._db["users"].delete_one({"_id": user_id})
        return res is not None and res.deleted_count != 0

    def list_users(self, limit: int = 50) -> List[User]:
        found = list(self._db["users"].find().limit(limit))
        return map(lambda x: User(**x), found)

    def add_user_to_project(
        self, user_id: str, project_id: str
    ) -> UserXProject:
        if self.get_user(user_id) is None:
            raise NotFoundError(f"User doesn't exist: {user_id}")
        if self.get_project(project_id) is None:
            raise NotFoundError(f"Project doesn't exist: {user_id}")
        uxp = UserXProject(user_id=user_id, project_id=project_id)
        model_dump = uxp.model_dump(by_alias=True)
        self._db["user_x_project"].insert_one(model_dump)
        return uxp

    def remove_user_from_project(self, user_id: str, project_id: str) -> bool:
        if self.get_user(user_id) is None:
            raise NotFoundError(f"User doesn't exist: {user_id}")
        if self.get_project(project_id) is None:
            raise NotFoundError(f"Project doesn't exist: {user_id}")

        uxp = UserXProject(user_id=user_id, project_id=project_id)
        found = self._db["user_x_project"].find_one({"_id": uxp.uuid})
        if not found:
            found = self._db["user_x_project"].find_one(
                {"user_id": user_id, "project_id": project_id}
            )
        if not found:
            return False

        res = self._db["user_x_project"].delete_one({"_id": uxp.uuid})
        return res is not None and res.deleted_count != 0

    def list_user_project_ids(self, user_id: str) -> List[UserXProject]:
        if self.get_user(user_id) is None:
            raise NotFoundError(f"User doesn't exist: {user_id}")
        found = self._db["user_x_project"].find({"user_id": user_id})
        return [uxp["project_id"] for uxp in found]


# Initialize DB
db = MongoDB()
