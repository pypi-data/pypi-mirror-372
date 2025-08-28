import shutil
import subprocess
import tempfile
from collections.abc import Generator
from functools import partial
from pathlib import Path
from typing import Callable

import pytest
from typer.testing import CliRunner

import plus_sync.cmd as ps_command
from plus_sync.pytest.factories.subject_file import SubjectFile, SubjectFileFactory

runner = CliRunner()


@pytest.fixture()
def plus_sync_to_temp_folder(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[Path]:
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.fixture(scope='function')
def plus_sync_cmd(plus_sync_to_temp_folder: Path) -> Callable:
    return partial(runner.invoke, ps_command.app)


@pytest.fixture(scope='function')
def plus_sync_initialized(plus_sync_cmd: Callable) -> Generator[Callable]:
    # remove config file if it exists
    Path('plus_sync.toml').unlink(missing_ok=True)
    # remove data folder recursively if it exists
    if Path('data_synced').exists():
        shutil.rmtree('data_synced')
    result = plus_sync_cmd(['init'], input='test\n')
    assert result.exit_code == 0
    assert 'Done' in result.stdout
    yield plus_sync_cmd


@pytest.fixture(scope='function')
def plus_sync_subjects_in_folder() -> Generator[Callable]:
    with tempfile.TemporaryDirectory() as tmpdir:

        def _subjects_in_folder(n_subjects: int, path: Path, lowercase: bool = True) -> tuple[list[SubjectFile], Path]:
            tmpdir_path = Path(tmpdir)
            subjects = SubjectFileFactory.create_batch(n_subjects, path=path, lowercase=lowercase)
            for subject in subjects:
                subject.save_to_disk(tmpdir_path)

            return subjects, tmpdir_path

        yield _subjects_in_folder


@pytest.fixture(scope='function')
def rclone_config(monkeypatch: pytest.MonkeyPatch) -> Generator[str]:
    rclone_config_remote_name = 'test'
    monkeypatch.setenv('RCLONE_CONFIG', 'rclone.conf')
    rclone('config', 'create', rclone_config_remote_name, 'local')
    yield rclone_config_remote_name
    Path('rclone.conf').unlink(missing_ok=True)


def rclone(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['rclone', '--config', 'rclone.conf', *args], capture_output=True, check=False)
