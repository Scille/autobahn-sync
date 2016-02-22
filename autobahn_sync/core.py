import crochet
from threading import Thread
from autobahn.twisted.wamp import Application, ApplicationSession, ApplicationRunner
from autobahn.wamp import message, types
from twisted.internet import defer

from .exceptions import AbortError, AlreadyRunningError

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


DEFAULT_AUTOBAHN_ROUTER = u"ws://127.0.0.1:8080/ws"
DEFAULT_AUTOBAHN_REALM = u"realm1"
crochet_initialized = False




class AutobahnSyncSession(object):
    """Synchronous subclass of :class:`autobahn.twisted.wamp._ApplicationSession`.
    """

    def __init__(self, async_session):
        print('BUILDING SYNC SESSION', async_session)
        self._async_session = async_session

    # @crochet.wait_for(timeout=30)
    # def disconnect(self):
    #     """Call a remote procedure.

    #     Replace :meth:`autobahn.wamp.interface.IApplicationSession.disconnect`
    #     """
    #     return super(AutobahnSyncSession, self).disconnect()

    @crochet.wait_for(timeout=30)
    def call(self, procedure, *args, **kwargs):
        """Call a remote procedure.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.call`
        """
        return self._async_session.call(procedure, *args, **kwargs)

    # def register(self, endpoint, procedure=None, options=None):
    #     """Register a procedure for remote calling.

    #     Replace :meth:`autobahn.wamp.interface.IApplicationSession.register`
    #     """
    #     reg = self._register(endpoint, procedure=procedure, options=options)
    #     # 
    #     async_unregister = reg.unregister
    #     from functools import wraps
    #     @crochet.wait_for(timeout=30)
    #     @wraps(reg.unregister)
    #     def wrapped_unregister():
    #         async_unregister()

    #     reg.unregister = wrapped_unregister
    #     return reg

    # @crochet.wait_for(timeout=30)
    # def _register(self, endpoint, procedure=None, options=None):
    #     return self._async_session.register(endpoint, procedure=procedure, options=options)

    @crochet.wait_for(timeout=30)
    def register(self, endpoint, procedure=None, options=None):
        """Register a procedure for remote calling.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.register`
        """
        return self._async_session.register(endpoint, procedure=procedure, options=options)

    @crochet.wait_for(timeout=30)
    def unregister(self, registration):
        return registration.unregister()

    @crochet.wait_for(timeout=30)
    def publish(self, topic, *args, **kwargs):
        """Publish an event to a topic.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.publish`
        """
        return self._async_session.publish(topic, *args, **kwargs)

    @crochet.wait_for(timeout=30)
    def subscribe(self, handler, topic=None, options=None):
        """Subscribe to a topic for receiving events.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.subscribe`
        """
        return self._async_session.subscribe(handler, topic=topic, options=options)

    def onMessage(self, msg):
        print('GOT ==>', msg)
        if isinstance(msg, message.Abort):
            details = types.CloseDetails(msg.reason, msg.message)
            raise ConnectionRefusedError(details)
        super(AutobahnSyncSession, self).onMessage(msg)


class _ApplicationSession(ApplicationSession):
    def __init__(self, config=None):
        super(_ApplicationSession, self).__init__(config=config)
        self.on_join_defer = defer.Deferred()

    def onMessage(self, msg):
        print('2 - ON MESSAGE ', msg)
        if not self.is_attached():
            if isinstance(msg, message.Abort):
                details = types.CloseDetails(msg.reason, msg.message)
                print('+++> Errback', msg)
                self.on_join_defer.errback(AbortError(details))
            else:
                print('+++> Callback', msg)
                self.on_join_defer.callback(msg)
        return super(_ApplicationSession, self).onMessage(msg)


def _init_crochet(in_twisted=False):
    global crochet_initialized
    if crochet_initialized:
        return
    if in_twisted:
        crochet.no_setup()
    else:
        crochet.setup()
    crochet_initialized = True


class ErrorCollector(object):
    def check(self):
        raise NotImplementedError()


class InTwistedErrorCollector(ErrorCollector):
    def __call__(self, failure):
        raise failure.value

    def check(self):
        pass


class OutTwistedErrorCollector(ErrorCollector):
    exception = None

    def __call__(self, failure):
        self.exception = failure.value
        raise failure.value

    def check(self):
        if self.exception:
            raise self.exception


class AutobahnSync(object):

    def __init__(self, prefix=None):
        self.session = None
        self._async_app = Application(prefix=prefix)
        self._async_runner = None
        self._async_session = None
        self._started = False
        self._error_collector_cls = None
        self._callback_thread = None
        self._callback_queue = Queue()

    def run(self, url=DEFAULT_AUTOBAHN_ROUTER, realm=DEFAULT_AUTOBAHN_REALM,
            in_twisted=False, blocking=False, **kwargs):
        """Start the background twisted thread and create the wamp connection

        .. note:: This function must be called first
        """
        if self._started:
            raise AlreadyRunningError("This AutobahnSync instance is already started")
        _init_crochet(in_twisted=in_twisted)

        if in_twisted:
            raise NotImplementedError()
            # self._in_twisted_start(url=url, realm=realm, **kwargs)
        else:
            self._out_twisted_start(url=url, realm=realm, **kwargs)
        self._started = True
        if blocking:
            self._run_callback_loop()
        else:
            # TODO: use twisted threadspool ?
            self._callback_thread = Thread(target=self._run_callback_loop)
            self._callback_thread.start()
            # Kill this thread once main have left
            crochet.register(self.stop)

    def stop(self):
        self._started = False
        # Add dummy function to force queue wakeup
        self._callback_queue.put(lambda: None)

    def _run_callback_loop(self):
        while self._started:
            # Get back and execute requested callbacks
            self._callback_queue.get()()

    # def _in_twisted_start(self, **kwargs):
    #     self._error_collector_cls = InTwistedErrorCollector
    #     self._async_runner = ApplicationRunner(**kwargs)
    #     d = self._async_runner.run(self._async_app, start_reactor=False)
    #     d.addErrback(self._error_collector_cls())

    def _out_twisted_start(self, **kwargs):

        @crochet.wait_for(timeout=30)
        def bootstrap():
            ready_deferred = defer.Deferred()
            print('START BOOTSTRAP')

            def register_session(config):
                print('START REGISTER SESSION')
                self._async_session = _ApplicationSession(config)
                self.session = AutobahnSyncSession(self._async_session)

                def resolve(result):
                    print('CALLED RESOLVE', result)
                    ready_deferred.callback(result)
                    return result

                self._async_session.on_join_defer.addCallback(resolve)

                def resolve_bad_end(failure):
                    print('CALLED RESOLVE (BAD END)', failure)
                    ready_deferred.errback(failure)

                self._async_session.on_join_defer.addErrback(resolve_bad_end)
                return self._async_session

            self._async_runner = ApplicationRunner(**kwargs)
            print('START RUNNER')
            d = self._async_runner.run(register_session, start_reactor=False)

            def connect_error(failure):
                ready_deferred.errback(failure)
                # return failure

            d.addErrback(connect_error)
            print('RUNNER STARTED')
            return ready_deferred

        print('0 - INIT')
        bootstrap()
        print('FINISHED')

    def register(self, procedure=None, options=None):
        "Decorator for the register"
        assert self.session
        def decorator(func):
            self.session.register(endpoint=func, procedure=procedure, options=options)
        return decorator

    def subscribe(self, topic, options=None):
        "Decorator for the subscribe"
        assert self.session
        def decorator(func):
            self.session.subscribe(handler=func, topic=topic, options=options)
        return decorator
