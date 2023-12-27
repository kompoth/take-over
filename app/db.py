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

    # ==== Project ====

    def save_project(self, project: Project) -> Project:
        model_dump = project.model_dump(by_alias=True)
        self._db["projects"].insert_one(model_dump)
        return project

    def get_project(self, project_id: str) -> Project | None:
        found = self._db["projects"].find_one({"_id": project_id})
        if not found:
            raise NotFoundError(f"Project doesn't exist: {project_id}")
        return Project(**found)

    def list_projects(self, limit: int = 50) -> List[Project]:
        found = list(self._db["projects"].find().limit(limit))
        return map(lambda x: Project(**x), found)

    def delete_project(self, project_id) -> bool:
        commits = self.get_project_commits(project_id)
        res = self._db["reports"].delete_many({
            "commit_id": {"$in": [co.uuid for co in commits]}
        })
        res = self._db["commits"].delete_many({"project_id": project_id})
        res = self._db["projects"].delete_one({"_id": project_id})
        return res is not None and res.deleted_count != 0

    # ==== Commit ====

    def save_commit(self, commit: Commit) -> Commit:
        self.get_project(commit.project_id)
        model_dump = commit.model_dump(by_alias=True)
        self._db["commits"].insert_one(model_dump)
        return commit
    
    def get_project_commits(self, project_id: str) -> List[Commit]:
        self.get_project(project_id)
        found = self._db["commits"].find({"project_id": project_id})
        return map(lambda x: Commit(**x), found)

    def get_commit(self, commit_id: str, do_raise: bool = True) -> Commit | None:
        found = self._db["commits"].find_one({"_id": commit_id})
        if not found and do_raise:
            raise NotFoundError(f"Commit doesn't exist: {commit_id}")
        return None if not found else Commit(**found)

    def get_last_commit(
        self, project_id: str, branch: str | None = None
    ) -> Commit | None:
        self.get_project(project_id)
        sort = [("dttm", -1)]
        selector = {"project_id": project_id}
        if branch:
            selector["branch"] = branch
        found = self._db["commits"].find(selector).sort(sort).limit(1)[0]
        return None if not found else Commit(**found)

    # ==== Report ====
    
    def save_report(self, rr: Report) -> Report:
        self.get_commit(rr.commit_id)
        model_dump = rr.model_dump(by_alias=True)
        self._db["reports"].insert_one(model_dump)
        return rr

    def get_reports(self, commit_id: str) -> List[Report]:
        self.get_commit(commit_id)
        selector = {"commit_id": commit_id}
        found = self._db["reports"].find(selector)
        return map(lambda x: Report(**x), found)

    # ==== User ====

    def get_user(self, user_id: str) -> User | None:
        found = self._db["users"].find_one({"_id": user_id})
        if not found:
            raise NotFoundError(f"User doesn't exist: {user_id}")
        return User(**found)

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

    # ==== Access rights ====

    def add_user_to_project(
        self, user_id: str, project_id: str
    ) -> UserXProject:
        self.get_user(user_id)
        self.get_project(project_id)
        uxp = UserXProject(user_id=user_id, project_id=project_id)
        model_dump = uxp.model_dump(by_alias=True)
        self._db["user_x_project"].insert_one(model_dump)
        return uxp

    def remove_user_from_project(self, user_id: str, project_id: str) -> bool:
        self.get_user(user_id)
        self.get_project(project_id)
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
        self.get_user(user_id)
        found = self._db["user_x_project"].find({"user_id": user_id})
        return [uxp["project_id"] for uxp in found]


# Initialize DB
db = MongoDB()
