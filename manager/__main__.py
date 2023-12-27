from typer import Typer

from manager.project import cli as project_cli

cli = Typer()
cli.add_typer(project_cli, name="project")


if __name__ == "__main__":
    cli()
