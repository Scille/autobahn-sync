from autobahn_sync import AutobahnSync, ConnectionRefusedError

from fixtures import crossbar


class Test(object):

    def test_connect(self, crossbar):
        wamp = AutobahnSync()
        wamp.start()

    def test_rpc(self, crossbar):
        wamp = AutobahnSync()
        rpc_calls = []
        token = '4242'

        @wamp.register('com.app.rpc')
        def my_rpc(e):
            assert e == 'arg'
            rpc_calls.append(token)
            return token

        # ret = wamp.call('com.app.rpc', 'arg')
        # assert rpc_called == [token]
