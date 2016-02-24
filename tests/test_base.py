import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError, AlreadyRunningError, TransportLost

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

    def test_leave(self, crossbar):
        wamp = AutobahnSync()
        wamp.run()
        wamp.session.publish('com.disconnect.ready')
        wamp.session.leave()
        with pytest.raises(TransportLost):
            wamp.session.publish('com.disconnect.no_realm')
