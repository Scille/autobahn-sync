import pytest

from autobahn_sync import AutobahnSync, ConnectionRefusedError


class TestBadRouter(object):

    def test_router_not_started(self):
        wamp = AutobahnSync()
        with pytest.raises(ConnectionRefusedError):
            wamp.start()
