from typing import Annotated

import typer

from ...config import Config
from ..app import app
from ..helpers.typer import HashSubjectIDs


@app.command(no_args_is_help=True)
def ls(
    remote_name: Annotated[str, typer.Argument(help='The name of the remote to use.')],
    hash_subject_ids: HashSubjectIDs,
) -> None:
    """
    List the files that are available.
    """
    typer.echo(f'Listing the projects for {remote_name}.')
    config = Config.from_cmdargs()
    sync = config.get_sync_by_name(remote_name)
    files = sync.get_files()

    if hash_subject_ids:
        [x.hash_subject_ids() for x in files]  # type: ignore

    for file in files:
        typer.echo(file)
