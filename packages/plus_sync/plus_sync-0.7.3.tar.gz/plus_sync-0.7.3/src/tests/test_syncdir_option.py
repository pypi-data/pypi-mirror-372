import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.mark.parametrize('syncdir', [True, False])
def test_syncdir_option(plus_sync_initialized, plus_sync_subjects_in_folder, rclone_config, syncdir):
    subjects, tmpdir_path = plus_sync_subjects_in_folder(3, 'testdata')
    plus_sync_initialized(
        ['add', 'rclone', 'test_rclone', rclone_config, str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt']
    )

    if Path('data_synced').exists():
        shutil.rmtree('data_synced')

    with TemporaryDirectory() as tmp_target:
        cmd = ['sync', 'test_rclone']
        if syncdir:
            cmd.extend(['--sync-folder', tmp_target])
        results = plus_sync_initialized(cmd)
        assert results.exit_code == 0

        if syncdir:
            assert Path(tmp_target).exists()
            assert Path(tmp_target).is_dir()
            for cur_subject in subjects:
                assert Path(tmp_target, 'test_rclone', cur_subject.hashed_filename).exists()
                assert not Path('data_synced', 'test_rclone', cur_subject.hashed_filename).exists()
        else:
            assert Path('data_synced').exists()
            assert Path('data_synced').is_dir()
            for cur_subject in subjects:
                assert Path('data_synced', 'test_rclone', cur_subject.hashed_filename).exists()
                assert not Path(tmp_target, 'test_rclone', cur_subject.hashed_filename).exists()
