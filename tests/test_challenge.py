import pytest
from time import sleep

from autobahn_sync import (AbortError,
    AutobahnSync, ConnectionRefusedError, NotRunningError,
    AlreadyRunningError, TransportLost)

from fixtures import crossbar, wamp


class TestChallenge(object):

    def test_no_auth_method(self, crossbar):
        wamp = AutobahnSync()
        with pytest.raises(AbortError) as exc:
            wamp.run(url=u'ws://localhost:8080/ws_auth', authmethods=[u'wampcra'])
        assert str(exc.value.args[0].reason) == 'wamp.error.no_auth_method'

    def test_bad_authid(self, crossbar):
        wamp = AutobahnSync()

        @wamp.on_challenge
        def on_challenge(challenge):
            pass

        with pytest.raises(AbortError) as exc:
            wamp.run(url=u'ws://localhost:8080/ws_auth', authid='dummy', authmethods=[u'ticket'])
        assert str(exc.value.args[0].reason) == 'wamp.error.not_authorized'

    def test_bad_method(self, crossbar):
        wamp = AutobahnSync()

        @wamp.on_challenge
        def on_challenge(challenge):
            raise Exception("Invalid authmethod %s" % challenge.method)

        with pytest.raises(AbortError) as exc:
            wamp.run(realm=u'realm1', url=u'ws://localhost:8080/ws_auth', authid='ticket_user_1', authmethods=[u'ticket'])
        assert str(exc.value.args[0]) == 'Invalid authmethod ticket'

    def test_good_auth(self, crossbar):
        wamp = AutobahnSync()

        @wamp.on_challenge
        def on_challenge(challenge):
            assert challenge.method == 'ticket'
            return 'ticket_secret'

        wamp.run(realm=u'realm1', url=u'ws://localhost:8080/ws_auth', authid='ticket_user_1', authmethods=[u'ticket'])
        # Make sure we are connected
        wamp.session.subscribe(lambda: None, u'test.challenge.event')
