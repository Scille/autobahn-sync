from os import path
from time import sleep
import subprocess
import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError


CROSSBAR_CONF_DIR = path.abspath(path.dirname(__file__)) + '/.crossbar'
START_CROSSBAR = not pytest.config.getoption("--no-router")


@pytest.fixture(scope="module")
def crossbar(request):
    if START_CROSSBAR:
        # Start a wamp router
        subprocess.Popen(["crossbar", "start", "--cbdir", CROSSBAR_CONF_DIR])
    started = False
    for _ in range(20):
        sleep(0.5)
        # Try to engage a wamp connection with crossbar to make sure it is started
        try:
            test_app = AutobahnSync()
            test_app.run()
            # test_app.session.disconnect()  # TODO: fix me
        except ConnectionRefusedError:
            continue
        else:
            started = True
            break
    if not started:
        raise RuntimeError("Couldn't connect to crossbar router")

    def finalizer():
        p = subprocess.Popen(["crossbar", "stop", "--cbdir", CROSSBAR_CONF_DIR])
        p.wait()

    if START_CROSSBAR:
        request.addfinalizer(finalizer)


@pytest.fixture
def wamp(crossbar):
    wamp = AutobahnSync()
    wamp.run()
    return wamp


@pytest.fixture
def wamp2(crossbar):
    return wamp(crossbar)
