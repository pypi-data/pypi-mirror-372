import json
import subprocess
from fnmatch import fnmatch
from typing import TYPE_CHECKING, Optional

from .base import BaseSync, FileInformation

if TYPE_CHECKING:
    import plus_sync.config


class RCloneAccess(BaseSync):
    def __init__(self, config: 'plus_sync.config.RCloneConfig'):
        self.config = config

    def _get_files(self, with_metadata: bool = True) -> list[FileInformation]:
        all_files = []
        this_files_json = self._rclone('lsjson', '-R', '--hash', self._remote_path())
        this_files = json.loads(this_files_json)
        this_files = [x for x in this_files if not x['IsDir']]
        this_files = [x for x in this_files if any(fnmatch(x['Path'], glob) for glob in self.config.globs)]
        this_files = [
            FileInformation(path=f'{x["Path"]}', size=x['Size'], last_modified=x['ModTime'], hashes=x['Hashes'])
            for x in this_files
        ]
        all_files.extend(this_files)

        return all_files

    def get_content(self, file: FileInformation) -> bytes:
        return subprocess.run(['rclone', 'cat', self._remote_path(file.path)], capture_output=True, check=False).stdout

    def _rclone(self, cmd: str, *args: str) -> str:
        return subprocess.run(['rclone', cmd, *args], capture_output=True, check=False).stdout.decode()

    def _remote_path(self, path: Optional[str] = None) -> str:
        p = f'{self.config.remote}:{self.config.remote_folder}'
        if path is not None:
            p = f'{p}/{path}'
        return p
