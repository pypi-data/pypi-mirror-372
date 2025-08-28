import typer

from ...config import Config
from ..app import app


@app.command()
def list_remotes() -> None:
    """
    List the available remotes.
    """
    config = Config.from_cmdargs()
    projects = config.get_all_config_names()
    for project in projects:
        typer.echo(project)
