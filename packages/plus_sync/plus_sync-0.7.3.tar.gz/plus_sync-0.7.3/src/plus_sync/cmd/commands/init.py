from typing import Annotated

import typer

from plus_sync.cmd.helpers.options import global_options
from plus_sync.config import Config

from ..app import app


@app.command()
def init(
    project_name: Annotated[str, typer.Option(help='The name of the project.', prompt=True)],
    overwrite: Annotated[bool, typer.Option(help='Overwrite the configuration file if it already exists.')] = False,
) -> None:
    """
    Initialize a new configuration file.
    """
    typer.echo(f'Initializing a new configuration file at {global_options["config_file"]}.')
    config = Config(project_name=project_name)
    if global_options['config_file'] is None:
        raise typer.Exit(code=1)
    try:
        config.save(global_options['config_file'], overwrite=overwrite)
    except FileExistsError:
        typer.echo('The file already exists. Use --overwrite to overwrite it.')
        raise typer.Exit(code=1)
    typer.echo('Done.')
