from pathlib import Path

from typer.testing import CliRunner

import plus_sync.cmd
import plus_sync.config

runner = CliRunner()


def test_init(plus_sync_to_temp_folder):
    result = runner.invoke(plus_sync.cmd.app, ['init'], input='test\n')
    assert result.exit_code == 0
    assert 'Done' in result.stdout
    assert Path('plus_sync.toml').exists()


def test_init_fixture(plus_sync_initialized):
    assert Path('plus_sync.toml').exists()
    assert 'project_name = "test"' in Path('plus_sync.toml').read_text()
