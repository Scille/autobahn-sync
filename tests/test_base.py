import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError, AlreadyRunningError

from fixtures import crossbar, wamp


class Test(object):

    def test_connect(self, crossbar):
        wamp = AutobahnSync()
        wamp.run()

    def test_already_running(self, crossbar):
        wamp = AutobahnSync()
        wamp.run()

        with pytest.raises(AlreadyRunningError):
            wamp.run()
