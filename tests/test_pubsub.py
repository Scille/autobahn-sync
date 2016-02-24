import pytest
from time import sleep

from autobahn_sync import AutobahnSync, ConnectionRefusedError, AbortError
from autobahn.wamp import PublishOptions, ApplicationError

from fixtures import crossbar, wamp, wamp2


class TestBadRouter(object):

    def test_no_subscribe(self, crossbar):
        wamp = AutobahnSync()
        wamp.run(realm=u'realm_limited')
        with pytest.raises(ApplicationError) as exc:
            wamp.session.subscribe(lambda: None, 'test.no_subscribe.event')
        assert str(exc.value.args[0]) == "session is not authorized to subscribe to topic 'test.no_subscribe.event'"

    @pytest.mark.xfail(reason='Must inverstigate in crossbar code...')
    def test_no_publish(self, crossbar):
        wamp = AutobahnSync()
        wamp.run(realm=u'realm_limited')
        wamp.session.subscribe(lambda: None, 'test.no_publish.event')
        with pytest.raises(ApplicationError):
            wamp.session.publish(u'test.no_publish.event', None)
        assert str(exc.value.args[0]) == u"session is not authorized to publish to topic'test.no_publish.event'"

    def test_use_session(self, wamp, wamp2):
        events = []

        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        sub = wamp2.session.subscribe(on_event, 'pubsub.use_session.event')
        ret = wamp.session.publish('pubsub.use_session.event', '1')
        ret = wamp.session.publish('pubsub.use_session.event', '2')
        ret = wamp.session.publish('pubsub.use_session.event', opt=True)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_single_wamp_use_session(self, wamp):
        events = []

        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        publish_opt = PublishOptions(exclude_me=False)
        sub = wamp.session.subscribe(on_event, 'pubsub.single_wamp_use_session.event')
        ret = wamp.session.publish('pubsub.single_wamp_use_session.event', '1', options=publish_opt)
        ret = wamp.session.publish('pubsub.single_wamp_use_session.event', '2', options=publish_opt)
        ret = wamp.session.publish('pubsub.single_wamp_use_session.event', opt=True, options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_use_decorator(self, wamp):
        events = []

        @wamp.subscribe('pubsub.use_decorator.event')
        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        publish_opt = PublishOptions(exclude_me=False)
        ret = wamp.session.publish('pubsub.use_decorator.event', '1', options=publish_opt)
        ret = wamp.session.publish('pubsub.use_decorator.event', '2', options=publish_opt)
        ret = wamp.session.publish('pubsub.use_decorator.event', opt=True, options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_decorate_before_run(self, crossbar):
        events = []
        wamp = AutobahnSync()

        @wamp.subscribe('pubsub.decorate_before_run.event')
        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        wamp.run()
        publish_opt = PublishOptions(exclude_me=False)
        ret = wamp.session.publish('pubsub.decorate_before_run.event', '1', options=publish_opt)
        ret = wamp.session.publish('pubsub.decorate_before_run.event', '2', options=publish_opt)
        ret = wamp.session.publish('pubsub.decorate_before_run.event', opt=True, options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]
