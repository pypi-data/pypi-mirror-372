from collections.abc import Generator

import pytest
from pytest_sftpserver.sftp.server import SFTPServer


@pytest.fixture
def sftp_fixture(sftpserver: SFTPServer) -> Generator:
    # https://github.com/ulope/pytest-sftpserver/issues/30
    # Tests hanging forever
    sftpserver.daemon_threads = True
    sftpserver.block_on_close = False
    yield sftpserver
