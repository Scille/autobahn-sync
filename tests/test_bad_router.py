import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError, AbortError
from autobahn.wamp.exception import ApplicationError

from fixtures import crossbar


class TestBadRouter(object):

    def test_router_not_started(self):
        wamp = AutobahnSync()
        with pytest.raises(ConnectionRefusedError):
            wamp.run(url=u'ws://localhost:9999/missing')
        # Make sure we can reuse the wamp object
        with pytest.raises(ConnectionRefusedError):
            wamp.run(url=u'ws://localhost:9999/missing')

    def test_bad_realm(self, crossbar):
        wamp = AutobahnSync()
        with pytest.raises(AbortError) as exc:
            wamp.run(realm=u'bad_realm')
        assert str(exc.value.args[0]) == 'CloseDetails(reason=<wamp.error.no_such_realm>, message=\'no realm "bad_realm" exists on this router\')'
