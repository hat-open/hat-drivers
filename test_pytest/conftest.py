import atexit
import subprocess
import time

import pytest


@pytest.fixture
def nullmodem(request, tmp_path):
    path1 = tmp_path / '1'
    path2 = tmp_path / '2'
    p = subprocess.Popen(['socat',
                          f'pty,link={path1},rawer',
                          f'pty,link={path2},rawer'],
                         stderr=subprocess.DEVNULL)
    while not path1.exists() or not path2.exists():
        time.sleep(0.001)

    def finalizer():
        p.terminate()

    atexit.register(finalizer)
    request.addfinalizer(finalizer)
    return path1, path2, p
