from pathlib import Path

import pytest


def test_limited_sync(plus_sync_cmd, plus_sync_initialized, rclone_config, plus_sync_subjects_in_folder):
    subjects, tmpdir_path = plus_sync_subjects_in_folder(3, 'testdata')
    plus_sync_cmd(['add', 'rclone', 'test_rclone', 'test', str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt'])

    subject_list_hashed = plus_sync_cmd(['list-subjects', 'test_rclone']).stdout
    subject_list_hashed = [x for x in subject_list_hashed.split('\n')[1:] if x]

    synced = plus_sync_cmd(['sync', 'test_rclone', '--limit=2'])
    assert synced.exit_code == 0
    assert 'Found 2 files, 2 need syncing.' in synced.stdout

    all_files = list(Path('data_synced/test_rclone').rglob('*.txt'))
    assert len(all_files) == 2  # noqa PLR2004

    synced_subject_ids = [x.stem[:12] for x in all_files]
    missing_subject = set(subject_list_hashed) - set(synced_subject_ids)
    assert len(missing_subject) == 1


@pytest.mark.parametrize('hashed', [True, False])
def test_limit_subjects_sync(plus_sync_initialized, rclone_config, plus_sync_subjects_in_folder, hashed):
    subjects, tmpdir_path = plus_sync_subjects_in_folder(5, 'testdata')
    plus_sync_initialized(
        ['add', 'rclone', 'test_rclone', rclone_config, str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt']
    )

    hash_param = '--hash-subject-ids' if hashed else '--no-hash-subject-ids'

    subjects_to_sync = [subjects[0], subjects[-1]]
    if hashed:
        subject_ids = [x.hashed_subject_id for x in subjects_to_sync]
    else:
        subject_ids = [x.subject_id for x in subjects_to_sync]

    limit_param_list = [f'--only-subject={x}' for x in subject_ids]

    synced = plus_sync_initialized(['sync', 'test_rclone', *limit_param_list, hash_param])

    assert synced.exit_code == 0

    all_files = list(Path('data_synced/test_rclone').rglob('*.txt'))
    assert len(all_files) == 2  # noqa PLR2004
    synced_subject_ids = [x.stem[:12] for x in all_files]

    assert set(synced_subject_ids) == set(subject_ids)


@pytest.mark.parametrize('hashed', [True, False])
def test_limit_subjects_wrong_subject(plus_sync_initialized, rclone_config, plus_sync_subjects_in_folder, hashed):
    subjects, tmpdir_path = plus_sync_subjects_in_folder(3, 'testdata')
    plus_sync_initialized(
        ['add', 'rclone', 'test_rclone', rclone_config, str(Path(tmpdir_path, 'testdata')), '--globs', '*.txt']
    )

    hash_param = '--hash-subject-ids' if hashed else '--no-hash-subject-ids'

    synced = plus_sync_initialized(['sync', 'test_rclone', '--only-subject=abc', hash_param])

    assert synced.exit_code == 1
    assert 'Subject' in synced.stdout
    assert 'not found' in synced.stdout
