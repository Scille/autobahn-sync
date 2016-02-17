from os import path
from time import sleep
import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError


CROSSBAR_CONF_DIR = path.abspath(__file__) + '/../.crossbar'


@pytest.fixture(scope="module")
def crossbar(request):
    import subprocess
    # Start a wamp router
    subprocess.Popen(["crossbar", "start", "--cbdir", CROSSBAR_CONF_DIR])
    started = False
    for _ in range(20):
        sleep(0.5)
        # Try to engage a wamp connection with crossbar to make sure it is started
        try:
            AutobahnSync().start()
        except ConnectionRefusedError:
            continue
        else:
            started = True
            break
    if not started:
        raise RuntimeError("Couldn't start crossbar router")

    def finalizer():
        p = subprocess.Popen(["crossbar", "stop", "--cbdir", CROSSBAR_CONF_DIR])
        p.wait()

    request.addfinalizer(finalizer)
