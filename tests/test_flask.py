import pytest

from flask import Flask
from time import sleep
from autobahn_sync.extensions.flask import FlaskAutobahnSync
from autobahn_sync import NotRunningError, AbortError, ConnectionRefusedError
from autobahn.wamp import PublishOptions

from fixtures import crossbar, wamp


class TestFlask(object):


    def setup(self):
        self.rpc_called = False
        self.sub_called = False

    def test_flask(self, crossbar):
        app = Flask(__name__)
        wamp = FlaskAutobahnSync()

        publish_opt = PublishOptions(exclude_me=False)

        @wamp.register('flask.flask.rpc')
        def rpc():
            self.rpc_called = True

        @wamp.subscribe('flask.flask.event')
        def sub():
            self.sub_called = True

        with pytest.raises(NotRunningError):
            wamp.session.call('flask.flask.rpc')

        with pytest.raises(NotRunningError):
            wamp.session.publish('flask.flask.event', options=publish_opt)

        assert not self.rpc_called
        assert not self.sub_called

        wamp.init_app(app)

        wamp.session.call('flask.flask.rpc')
        wamp.session.publish('flask.flask.event', options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...

        assert self.rpc_called
        assert self.sub_called

    def test_bad_config(self):
        app = Flask(__name__)
        with pytest.raises(AbortError):
            wamp = FlaskAutobahnSync(app, realm=u'bad_realm')
        with pytest.raises(ConnectionRefusedError):
            wamp = FlaskAutobahnSync(app, router=u'ws://localhost:9999/missing')
