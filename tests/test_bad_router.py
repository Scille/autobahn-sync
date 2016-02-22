import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError, AbortError
from autobahn.wamp.exception import ApplicationError


class TestBadRouter(object):

    def test_router_not_started(self):
        wamp = AutobahnSync()
        with pytest.raises(ConnectionRefusedError):
            wamp.run(url=u'ws://localhost:9999/missing')

    def test_bad_realm(self):
        wamp = AutobahnSync()
        with pytest.raises(AbortError) as exc:
            wamp.run(realm=u'bad_realm')
        assert str(exc.value.message) == 'CloseDetails(reason=<wamp.error.no_such_realm>, message=\'no realm "bad_realm" exists on this router\')'
