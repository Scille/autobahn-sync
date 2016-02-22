import crochet
from threading import Thread
from autobahn.twisted.wamp import Application, ApplicationRunner
from twisted.internet import defer

from .exceptions import AlreadyRunningError
from .session import SyncSession, AsyncSession

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


DEFAULT_AUTOBAHN_ROUTER = u"ws://127.0.0.1:8080/ws"
DEFAULT_AUTOBAHN_REALM = u"realm1"
crochet_initialized = False


def _init_crochet(in_twisted=False):
    global crochet_initialized
    if crochet_initialized:
        return
    if in_twisted:
        crochet.no_setup()
    else:
        crochet.setup()
    crochet_initialized = True


# class ErrorCollector(object):
#     def check(self):
#         raise NotImplementedError()


# class InTwistedErrorCollector(ErrorCollector):
#     def __call__(self, failure):
#         raise failure.value

#     def check(self):
#         pass


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
                self._async_session = AsyncSession(config)
                self.session = SyncSession(self._async_session)

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
