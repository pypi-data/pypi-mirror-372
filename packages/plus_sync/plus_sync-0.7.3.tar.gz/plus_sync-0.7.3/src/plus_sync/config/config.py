from abc import ABC
from typing import TYPE_CHECKING, Optional

import cattrs
import typer
from attrs import define

from plus_sync.config.abstract import AbstractTomlConfig
from plus_sync.config.helpers import validate_duplicate_names, validated_field

if TYPE_CHECKING:
    import plus_sync.sync.base

cattrs_converter = cattrs.Converter(forbid_extra_keys=True)


@define(kw_only=True)
class BaseRemoteConfig(ABC):
    default_globs = ['*.mat', '*.fif']

    name: str = validated_field(metadata={'typer_annotation': typer.Argument(help='The name of this remote')})
    globs: list[str] = validated_field(
        metadata={
            'typer_annotation': typer.Option(help='The pattern used to match the files. Can be used multiple times.')
        }
    )

    @globs.default
    def _default_globs(self) -> list[str]:
        return self.default_globs


@define(kw_only=True)
class GitlabConfig(BaseRemoteConfig):
    default_globs = ['*.mat']

    slug: str = validated_field(metadata={'typer_annotation': typer.Argument(help='The slug of the project')})
    paths: list[str] = validated_field(
        metadata={'typer_annotation': typer.Argument(help='The paths to use. Can be used multiple times')}
    )
    branch: str = validated_field(
        default='main', metadata={'typer_annotation': typer.Option(help='The branch to use.')}
    )
    host: str = validated_field(
        default='https://gitlab.com',
        metadata={'typer_annotation': typer.Option(help='The host of the Gitlab instance.')},
    )
    token_file: str = validated_field(
        default='.gitlab_token',
        metadata={'typer_annotation': typer.Option(help='The file containing the Gitlab token.')},
    )


@define(kw_only=True)
class SFTPConfig(BaseRemoteConfig):
    host: str = validated_field(metadata={'typer_annotation': typer.Argument(help='The host of the SFTP server.')})
    user: str = validated_field(
        metadata={'typer_annotation': typer.Argument(help='The user to use for the SFTP server.')}
    )
    remote_folder: str = validated_field(
        metadata={
            'typer_annotation': typer.Argument(
                help='The remote folder to use. (e.g. /mnt/sinuhe/data_raw/project_name)'
            )
        }
    )
    port: int = validated_field(
        default=22, metadata={'typer_annotation': typer.Option(help='The port of the SFTP server.')}
    )


@define(kw_only=True)
class RCloneConfig(BaseRemoteConfig):
    remote: str = validated_field(metadata={'typer_annotation': typer.Argument(help='The rclone remote to use.')})
    remote_folder: str = validated_field(
        metadata={'typer_annotation': typer.Argument(help='The remote folder to use.')}
    )


@define()
class Config(AbstractTomlConfig):
    project_name: str = validated_field()
    sync_folder: str = validated_field(default='data_synced')
    subject_id_regex: str = validated_field(default=r'[12][0-9]{7}[a-zA-Z]{4}')
    hash_subject_ids: bool = validated_field(default=True)
    SFTP: Optional[list[SFTPConfig]] = validated_field(default=None, validator=validate_duplicate_names)
    Gitlab: Optional[list[GitlabConfig]] = validated_field(default=None, validator=validate_duplicate_names)
    RClone: Optional[list[RCloneConfig]] = validated_field(default=None, validator=validate_duplicate_names)

    def get_all_config_names(self) -> list[str]:
        names = []

        if self.SFTP is not None:
            names.extend([x.name for x in self.SFTP])

        if self.Gitlab is not None:
            names.extend([x.name for x in self.Gitlab])

        if self.RClone is not None:
            names.extend([x.name for x in self.RClone])

        return names

    def get_config_by_name(self, name: str) -> SFTPConfig | GitlabConfig | RCloneConfig:
        if self.SFTP is not None:
            for sftp in self.SFTP:
                if sftp.name == name:
                    return sftp

        if self.Gitlab is not None:
            for gitlab in self.Gitlab:
                if gitlab.name == name:
                    return gitlab

        if self.RClone is not None:
            for rclone in self.RClone:
                if rclone.name == name:
                    return rclone

        raise ValueError(f'No configuration with name {name} found.')

    def get_sync_by_name(self, name: str) -> 'plus_sync.sync.base.BaseSync':
        from plus_sync.sync.base import BaseSync  # noqa PLC0415

        cfg = self.get_config_by_name(name)
        return BaseSync.get_from_config(cfg)

    @classmethod
    def _get_config_file(cls) -> str:
        from plus_sync.cmd.helpers.options import global_options  # noqa PLC0415

        if global_options['config_file'] is None:
            raise ValueError('Config file not set.')

        return global_options['config_file']
