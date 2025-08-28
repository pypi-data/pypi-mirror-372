import shutil
from pathlib import Path

import pytest

import plus_sync.config


def create_command(cmd, hash_cmd_option) -> list[str]:
    cmd_list = [cmd, 'test_rclone']
    if hash_cmd_option is not None:
        cmd_list.append('--hash-subject-ids' if hash_cmd_option else '--no-hash-subject-ids')

    return cmd_list


@pytest.mark.parametrize('hash_subject_ids', [True, False])
def test_no_hash_config_option(plus_sync_initialized, hash_subject_ids, plus_sync_subjects_in_folder, rclone_config):
    config = plus_sync.config.Config.from_toml('plus_sync.toml')
    config.hash_subject_ids = hash_subject_ids
    config.save('plus_sync.toml', overwrite=True)

    assert 'hash_subject_ids = ' + str(hash_subject_ids).lower() in Path('plus_sync.toml').read_text()

    subjects, tmpdir_path = plus_sync_subjects_in_folder(3, 'testdata')
    plus_sync_initialized(
        ['add', 'rclone', 'test_rclone', rclone_config, str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt']
    )

    for hash_cmd_option in (None, True, False):
        cmd = create_command('list-subjects', hash_cmd_option)
        results = plus_sync_initialized(cmd)
        assert results.exit_code == 0
        assert '3 subjects' in results.stdout

        should_be_hashed = hash_subject_ids if hash_cmd_option is None else hash_cmd_option

        for current_subject in subjects:
            if should_be_hashed:
                assert current_subject.hashed_subject_id in results.stdout
                assert current_subject.subject_id not in results.stdout
            else:
                assert current_subject.subject_id in results.stdout
                assert current_subject.hashed_subject_id not in results.stdout

        cmd = create_command('ls', hash_cmd_option)
        results = plus_sync_initialized(cmd)
        assert results.exit_code == 0
        for current_subject in subjects:
            if should_be_hashed:
                assert current_subject.hashed_subject_id in results.stdout
                assert current_subject.subject_id not in results.stdout
            else:
                assert current_subject.subject_id in results.stdout
                assert current_subject.hashed_subject_id not in results.stdout

        if Path('data_synced').exists():
            shutil.rmtree('data_synced')
        cmd = create_command('sync', hash_cmd_option)
        results = plus_sync_initialized(cmd)
        assert results.exit_code == 0

        for current_subject in subjects:
            if should_be_hashed:
                assert Path('data_synced/test_rclone', current_subject.hashed_filename).exists()
                assert not Path('data_synced/test_rclone', current_subject.filename).exists()
            else:
                assert Path('data_synced/test_rclone', current_subject.filename).exists()
                assert not Path('data_synced/test_rclone', current_subject.hashed_filename).exists()
