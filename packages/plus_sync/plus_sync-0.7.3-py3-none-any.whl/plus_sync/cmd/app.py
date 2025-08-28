from typing import Annotated

import typer

from plus_sync.__version__ import __version__
from plus_sync.cmd.helpers.options import global_options

app = typer.Typer(no_args_is_help=True, rich_markup_mode='rich')


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f'plus_sync {__version__}')
        raise typer.Exit()


@app.callback()
def common(
    config_file: Annotated[
        str,
        typer.Option(
            help='The configuration file to use.',
            envvar='PLUS_SYNC_CONFIG_FILE',
        ),
    ] = 'plus_sync.toml',
    version: bool = typer.Option(
        None, '--version', help='Display current version of plus_sync and exit.', callback=version_callback
    ),
) -> None:
    """
    Sync data between Gitlab and SinuheMEG or anything else that can be
    reached via gitlab, SFTP or rsync.

    Enter plus_sync init to get started.
    """
    global_options['config_file'] = config_file
