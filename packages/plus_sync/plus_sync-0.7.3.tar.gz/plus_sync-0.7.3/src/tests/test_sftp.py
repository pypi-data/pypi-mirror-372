from plus_sync.pytest.factories.subject_file import SubjectFile, SubjectFileFactory
from tests.helpers.sync import sync_tester


def test_simple_sftp(plus_sync_initialized, sftp_fixture):
    result = plus_sync_initialized(
        [
            'add',
            'sftp',
            'test_sftp',
            sftp_fixture.host,
            'user',
            '/testdata/',
            '--port',
            sftp_fixture.port,
            '--globs',
            '*.txt',
        ]
    )
    assert result.exit_code == 0
    assert 'Done' in result.stdout

    result = plus_sync_initialized(['list-remotes'])
    assert result.exit_code == 0
    assert 'test_sftp' in result.stdout

    subject_files = SubjectFileFactory.create_batch(3, path='/testdata')

    all_content = SubjectFile.create_content_for_sftp(subject_files)

    with sftp_fixture.serve_content(all_content):
        sync_tester(plus_sync_initialized, subject_files, 'test_sftp', input='pw\n')
