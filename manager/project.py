import json
from typing_extensions import Annotated
from pathlib import Path
from typer import Typer, Argument, Option, Abort, confirm
from rich.console import Console
from rich.table import Table

from app.db import db, ExistsError
from app.models import Project

console = Console()
cli = Typer()


@cli.command("ls")
def list_projects(
    limit: Annotated[int, Argument(help="Max number of projects to list")] = 50
):
    """List projects"""
    projects = db.list_projects() 
    table = Table("id", "name", "url") 
    for proj in projects:
        table.add_row(proj.uuid, proj.name, proj.url)
    console.print(table)


@cli.command("delete")
def delete_project(
    project_id: Annotated[str, Argument(help="Project ID")]
):
    """Delete project and all its data"""
    sure = confirm("Sure you want to delete this project with all its data?")
    if not sure:
        raise Abort()
    result = db.delete_project(project_id)


@cli.command("create")
def create_project(
    path: Annotated[Path, Argument(help="JSON with project definition")]
):
    if not path.exists() or path.is_dir():
        print("File doesn't exist or is a directory")
        raise Abort()

    with open(path.absolute(), "r") as fd:
        proj_json = json.load(fd)
    try:
        project = db.save_project(Project(**proj_json))

    except ExistsError as err:
        print(str(err))
        raise Abort()
    print(f"Created project {project.uuid}")


if __name__ == "__main__":
    cli()
