import pytest
from time import sleep

from autobahn.wamp import PublishOptions
from autobahn_sync import run, register, subscribe, publish, call, NotRunningError

from fixtures import crossbar, wamp


class TestApi(object):

    def setup(self):
        self.rpc_called = False
        self.sub_called = False

    def test_api(self, crossbar):
        publish_opt = PublishOptions(exclude_me=False)

        @register('api.api.rpc')
        def rpc():
            self.rpc_called = True

        @subscribe('api.api.event')
        def sub():
            self.sub_called = True

        with pytest.raises(NotRunningError):
            call('api.api.rpc')

        with pytest.raises(NotRunningError):
            publish('api.api.event', options=publish_opt)

        assert not self.rpc_called
        assert not self.sub_called

        run()

        call('api.api.rpc')
        publish('api.api.event', options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...

        assert self.rpc_called
        assert self.sub_called
