import pytest

from autobahn_sync import AutobahnSync
from autobahn.wamp.exception import ApplicationError

from fixtures import crossbar, wamp, wamp2


class CounterHelper(object):
    def __init__(self):
        self.counter = 0

    def __call__(self):
        self.counter += 1
        return self.counter


class TestRPC(object):

    def test_no_register(self):
        wamp = AutobahnSync()
        wamp.run(realm=u'realm_limited')
        with pytest.raises(ApplicationError) as exc:
            wamp.session.register(lambda: None, u'test.no_register.func')
        assert str(exc.value.message) == u"session is not authorized to register procedure 'test.no_register.func'"

    @pytest.mark.xfail(reason='Must inverstigate in crossbar code...')
    def test_no_call(self):
        wamp = AutobahnSync()
        wamp.run(realm=u'realm_limited')
        wamp.session.register(lambda: None, u'test.no_call.func')
        with pytest.raises(ApplicationError) as exc:
            wamp.session.call(u'test.no_call.func', None)
        assert str(exc.value.message) == u"session is not authorized to call procedure 'test.no_register.func'"

    def test_history(self, wamp):
        # First create some stuff in the history
        ret = wamp.session.publish('com.historized.event', 1)
        ret = wamp.session.publish('com.historized.event', '2')
        ret = wamp.session.publish('com.historized.event', args=True)

        # Arriving too late to get notified of the events...
        sub = wamp.session.subscribe(lambda: None, 'com.historized.event')
        # ...but history is here for this !
        events = wamp.session.call('wamp.subscription.get_events', sub.id, 3)

        assert len(events) == 3
        assert not [e for e in events if e[u'topic'] != u'com.historized.event']
        assert [e[u'kwargs'] for e in events] == [{'args': True}, None, None]
        assert [e[u'args'] for e in events] == [[], ['2'], [1]]

    def test_bad_history(self, wamp):
        # Cannot get history on this one, should raise exception then
        sub = wamp.session.subscribe(lambda: None, 'com.not_historized.event')
        with pytest.raises(ApplicationError) as exc:
            events = wamp.session.call('wamp.subscription.get_events', sub.id, 10)
        assert str(exc.value.error_message()) == u'wamp.error.history_unavailable: '

    def test_use_session(self, wamp, wamp2):
        rets = []
        counter_func = CounterHelper()
        sub = wamp2.session.register(counter_func, 'com.use_session.func')
        rets.append(wamp.session.call('com.use_session.func'))
        rets.append(wamp.session.call('com.use_session.func'))
        rets.append(wamp.session.call('com.use_session.func'))
        assert rets == [1, 2, 3]

    def test_unregister(self, wamp, wamp2):
        reg = wamp2.session.register(lambda: None, 'com.unregister.func')
        wamp.session.call('com.unregister.func')
        # reg.unregister()  # Cannot use the default API so far...
        wamp.session.unregister(reg)
        # with pytest.raises():
        with pytest.raises(ApplicationError) as exc:
            wamp.session.call('com.unregister.func')
        assert str(exc.value.message) == u'no callee registered for procedure <com.unregister.func>'
        # Cannot unregister 2 times
        with pytest.raises(Exception) as exc:
            wamp.session.unregister(reg)
        assert str(exc.value.message) == 'registration no longer active'

    def test_single_wamp_use_session(self, wamp):
        rets = []
        counter_func = CounterHelper()
        sub = wamp.session.register(counter_func, 'com.single_wamp_use_session.func')
        rets.append(wamp.session.call('com.single_wamp_use_session.func'))
        rets.append(wamp.session.call('com.single_wamp_use_session.func'))
        rets.append(wamp.session.call('com.single_wamp_use_session.func'))
        assert rets == [1, 2, 3]

    def test_use_decorator(self, wamp):
        rets = []
        counter_func = CounterHelper()

        @wamp.register(u'com.use_decorator.func')
        def my_func(*args, **kwargs):
            return counter_func()

        rets.append(wamp.session.call('com.use_decorator.func'))
        rets.append(wamp.session.call('com.use_decorator.func'))
        rets.append(wamp.session.call('com.use_decorator.func'))
        assert rets == [1, 2, 3]

    @pytest.mark.xfail(reason='Need lazy decorator registration first')
    def test_decorate_before_run(self):
        wamp = AutobahnSync()
        rets = []
        counter_func = CounterHelper()

        @wamp.register('com.decorate_before_run.func')
        def my_func(*args, **kwargs):
            return counter_func()

        wamp.run()
        rets.append(wamp.session.call('com.decorate_before_run.func'))
        rets.append(wamp.session.call('com.decorate_before_run.func'))
        rets.append(wamp.session.call('com.decorate_before_run.func'))
        assert rets == [1, 2, 3]
