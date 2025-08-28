import typer

from plus_sync.cmd.helpers.decorators import inject_attrs
from plus_sync.cmd.helpers.options import global_options
from plus_sync.config import Config, GitlabConfig, RCloneConfig, SFTPConfig

from ..app import app

add_app = typer.Typer(no_args_is_help=True, rich_markup_mode='rich')


@add_app.command(no_args_is_help=True)
@inject_attrs(GitlabConfig)
def gitlab(gitlab_config: GitlabConfig) -> None:
    """
    Add a remote for a gitlab hosted project.


    This remote requires setting up a personal access token in Gitlab. If you use gitlab.com
    you can create one by going to https://gitlab.com/-/user_settings/personal_access_tokens.
    Make sure to choose the `read_api` scope.
    After the creation process, it will show you the token. Save this token into `.gitlab_token`.

    You are also going to need the slug of the project. This is the part of the URL that comes after
    the host. For example, in the URL https://gitlab.com/username/project the slug is username/project.

    If you want to use a different host like the ANC or a self hosted gitlab instance, you can specify
    the host with the `--host` option.

    """
    config = Config.from_cmdargs()
    if not config.Gitlab:
        config.Gitlab = []

    config.Gitlab.append(gitlab_config)
    if global_options['config_file'] is None:
        raise typer.Exit(code=1)
    config.save(global_options['config_file'], overwrite=True)
    typer.echo('Done')


@add_app.command(no_args_is_help=True)
@inject_attrs(SFTPConfig)
def sftp(sftp_config: SFTPConfig) -> None:
    """
    Add a SFTP remote.

    In order to do passwordless login, you need to setup a ssh key pair and add the
    configuration to your [italic]~/.ssh/config[/italic] file.

    If no ssh configuration is present, you need to enter the password every time
    you use the remote.
    """
    config = Config.from_cmdargs()
    if not config.SFTP:
        config.SFTP = []

    config.SFTP.append(sftp_config)
    if global_options['config_file'] is None:
        raise typer.Exit(code=1)
    config.save(global_options['config_file'], overwrite=True)
    typer.echo('Done')


@add_app.command(no_args_is_help=True)
@inject_attrs(RCloneConfig)
def rclone(rclone_config: RCloneConfig) -> None:
    """
    Add a RClone remote.

    This remote uses [italic]rclone[/italic] to sync data. You need to have rclone installed and
    also configure an "rclone remote". You can find more information on how to do this [link=https://rclone.org/docs/]here[/link].
    As you can see, you can use a wide variety of protocols, services and so on with rclone.
    """
    config = Config.from_cmdargs()
    if not config.RClone:
        config.RClone = []

    config.RClone.append(rclone_config)
    if global_options['config_file'] is None:
        raise typer.Exit(code=1)
    config.save(global_options['config_file'], overwrite=True)
    typer.echo('Done')


app.add_typer(add_app, name='add', help='Add new synchronisation items.')
