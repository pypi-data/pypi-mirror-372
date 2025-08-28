from pathlib import Path
from typing import Callable, Optional

import plus_sync.pytest.factories.subject_file


def sync_tester(
    plus_sync: Callable,
    subject_files: list[plus_sync.pytest.factories.subject_file.SubjectFile],
    remote_name: str,
    input: Optional[str] = None,
):
    result = plus_sync(['ls', remote_name, '--no-hash-subject-ids'], input=input)
    assert result.exit_code == 0
    assert all(f.subject_id in result.stdout for f in subject_files)
    result = plus_sync(['list-subjects', remote_name, '--no-hash-subject-ids'], input=input)
    assert result.exit_code == 0
    assert all(f.subject_id in result.stdout for f in subject_files)

    result = plus_sync(['list-subjects', remote_name], input=input)
    assert result.exit_code == 0
    assert all(f.subject_id not in result.stdout for f in subject_files)
    assert all(f.hashed_subject_id in result.stdout for f in subject_files)

    result = plus_sync(['sync', remote_name], input=input)
    assert result.exit_code == 0
    assert all(Path('data_synced', remote_name, f.hashed_filename).exists() for f in subject_files)
