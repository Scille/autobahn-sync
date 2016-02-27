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
            wamp.session.subscribe(lambda: None, 'pubsub.no_subscribe.event')
        assert str(exc.value.args[0]) == "session is not authorized to subscribe to topic 'pubsub.no_subscribe.event'"

    def test_no_publish(self, crossbar):
        wamp = AutobahnSync()
        wamp.run(realm=u'realm_limited')
        wamp.session.subscribe(lambda: None, 'pubsub.no_publish.event')
        publish_opt = PublishOptions(acknowledge=True)
        with pytest.raises(ApplicationError) as exc:
            res = wamp.session.publish(u'pubsub.no_publish.event', None, options=publish_opt)
        assert str(exc.value.args[0]) == u"session not authorized to publish to topic 'pubsub.no_publish.event'"

    def test_use_session(self, wamp, wamp2):
        events = []

        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        sub = wamp2.session.subscribe(on_event, 'pubsub.use_session.event')
        wamp.session.publish('pubsub.use_session.event', '1')
        wamp.session.publish('pubsub.use_session.event', '2')
        wamp.session.publish('pubsub.use_session.event', opt=True)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_single_wamp_use_session(self, wamp):
        events = []

        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        publish_opt = PublishOptions(exclude_me=False)
        sub = wamp.session.subscribe(on_event, 'pubsub.single_wamp_use_session.event')
        wamp.session.publish('pubsub.single_wamp_use_session.event', '1', options=publish_opt)
        wamp.session.publish('pubsub.single_wamp_use_session.event', '2', options=publish_opt)
        wamp.session.publish('pubsub.single_wamp_use_session.event', opt=True, options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_use_decorator(self, wamp):
        events = []

        @wamp.subscribe(u'pubsub.use_decorator.event')
        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        publish_opt = PublishOptions(exclude_me=False)
        wamp.session.publish('pubsub.use_decorator.event', '1', options=publish_opt)
        wamp.session.publish('pubsub.use_decorator.event', '2', options=publish_opt)
        wamp.session.publish('pubsub.use_decorator.event', opt=True, options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_decorate_before_run(self, crossbar):
        events = []
        wamp = AutobahnSync()

        @wamp.subscribe(u'pubsub.decorate_before_run.event')
        def on_event(*args, **kwargs):
            events.append((args, kwargs))

        wamp.run()
        publish_opt = PublishOptions(exclude_me=False)
        wamp.session.publish('pubsub.decorate_before_run.event', '1', options=publish_opt)
        wamp.session.publish('pubsub.decorate_before_run.event', '2', options=publish_opt)
        wamp.session.publish('pubsub.decorate_before_run.event', opt=True, options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {}), (('2',), {}), ((), {'opt': True})]

    def test_on_exception(self, wamp):
        events = []
        class MyException(Exception):
            pass

        @wamp.subscribe(u'pubsub.on_exception.event')
        def on_event(*args, **kwargs):
            events.append((args, kwargs))
            raise MyException('Ooops !')

        publish_opt = PublishOptions(exclude_me=False, acknowledge=True)
        wamp.session.publish('pubsub.on_exception.event', '1', options=publish_opt)
        sleep(0.1)  # Dirty way to wait for on_event to be called...
        assert events == [(('1',), {})]
