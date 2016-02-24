import pytest

from autobahn_sync import (
    AutobahnSync, ConnectionRefusedError, NotRunningError,
    AlreadyRunningError, TransportLost)

from fixtures import crossbar, wamp


class Test(object):

    def test_connect(self, crossbar):
        wamp = AutobahnSync()
        wamp.run()

    def test_get_session(self, crossbar):
        wamp = AutobahnSync()
        with pytest.raises(NotRunningError) as exc:
            wamp.session
        assert str(exc.value.args[0]) == 'No session available, is AutobahnSync running ?'

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
