import crochet
from autobahn.twisted.wamp import ApplicationRunner
from twisted.internet import defer, threads

from .logger import logger
from .exceptions import AlreadyRunningError, NotRunningError
from .session import SyncSession, _AsyncSession
from .callbacks_runner import CallbacksRunner, ThreadedCallbacksRunner


__all__ = ('DEFAULT_AUTOBAHN_ROUTER', 'DEFAULT_AUTOBAHN_REALM', 'AutobahnSync')


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


class AutobahnSync(object):

    """
    Main class representing the AutobahnSync application
    """

    def __init__(self, prefix=None):
        self._session = None
        self._async_runner = None
        self._async_session = None
        self._started = False
        self._callbacks_runner = None
        self._on_running_callbacks = []

    @property
    def session(self):
        """Return the underlying :class:`session.SyncSession`
        object if available or raise an :class:`exceptions.NotRunningError`
        """
        if not self._session:
            raise NotRunningError("No session available, is AutobahnSync running ?")
        return self._session

    def run_in_twisted(self, callback=None, url=DEFAULT_AUTOBAHN_ROUTER,
                       realm=DEFAULT_AUTOBAHN_REALM, **kwargs):
        """
        Start the WAMP connection. Given we cannot run synchronous stuff inside the
        twisted thread, use this function (which returns immediately) to do the
        initialization from a spawned thread.

        :param callback: function that will be called inside the spawned thread.
        Put the rest of you init (or you main loop if you have one) inside it

        .. note::
            This function must be called instead of :meth:`AutobahnSync.run`
            if we are calling from twisted application (typically if we are running
            our application inside crossbar as a `wsgi` component)
        """
        _init_crochet(in_twisted=True)
        logger.debug('run_in_crossbar, bootstraping')
        # No need to go non-blocking if no callback has been provided
        blocking = callback is None

        def bootstrap_and_callback():
            self._bootstrap(blocking, url=url, realm=realm, **kwargs)
            if callback:
                callback()
            self._callbacks_runner.start()

        threads.deferToThread(bootstrap_and_callback)

    def run(self, callback=None, url=DEFAULT_AUTOBAHN_ROUTER, realm=DEFAULT_AUTOBAHN_REALM,
            blocking=False, **kwargs):
        """
        Start the background twisted thread and create the WAMP connection

        :param blocking: If ``False`` (default) this method will spawn a new
        thread that will be used to run the callback events (e.i. registered and
        subscribed functions). If ``True`` this method will not returns and
        use the current thread to run the callbacks.
        :param callback: This callback will be called once init is done, use it
        with ``blocking=True`` to put your WAMP related init
        """
        _init_crochet(in_twisted=False)
        self._bootstrap(blocking, url=url, realm=realm, **kwargs)
        if callback:
            callback()
        self._callbacks_runner.start()

    def stop(self):
        """
        Terminate the WAMP session

        .. note::
            If the :meth:`AutobahnSync.run` has been run with ``blocking=True``,
            it will returns then.
        """
        if not self._started:
            raise NotRunningError("This AutobahnSync instance is not started")
        self._callbacks_runner.stop()
        self._started = False

    def _bootstrap(self, blocking, **kwargs):
        """Synchronous bootstrap (even if `blocking=False` is provided !)

        Create the WAMP session and configure the `_callbacks_runner`.
        """
        if self._started:
            raise AlreadyRunningError("This AutobahnSync instance is already started")
        self._started = True
        if blocking:
            self._callbacks_runner = CallbacksRunner()
        else:
            self._callbacks_runner = ThreadedCallbacksRunner()

        @crochet.wait_for(timeout=30)
        def start_runner():
            ready_deferred = defer.Deferred()
            logger.debug('[CrochetReactor] start bootstrap')

            def register_session(config):
                logger.debug('[CrochetReactor] start register_session')
                self._async_session = _AsyncSession(config=config)
                self._session = SyncSession(self._async_session, self._callbacks_runner)

                def resolve(result):
                    logger.debug('[CrochetReactor] callback resolve: %s' % result)
                    ready_deferred.callback(result)
                    return result

                self._async_session.on_join_defer.addCallback(resolve)

                def resolve_error(failure):
                    logger.debug('[CrochetReactor] errback resolve_error: %s' % failure)
                    ready_deferred.errback(failure)

                self._async_session.on_join_defer.addErrback(resolve_error)
                return self._async_session

            self._async_runner = ApplicationRunner(**kwargs)
            d = self._async_runner.run(register_session, start_reactor=False)

            def connect_error(failure):
                ready_deferred.errback(failure)

            d.addErrback(connect_error)
            logger.debug('[CrochetReactor] end bootstrap')
            return ready_deferred

        logger.debug('[MainThread] call bootstrap')
        start_runner()
        logger.debug('[MainThread] call decorated register/subscribe')
        for cb in self._on_running_callbacks:
            cb()
        self._on_running_callbacks = []
        logger.debug('[MainThread] start callbacks runner')

    def register(self, procedure=None, options=None):
        """Decorator for the :meth:`AutobahnSync.session.register`

        .. note::
            This decorator can be used before :meth:`AutobahnSync.run` is called.
            In such case the actual registration will be done at ``run()`` time.
        """

        def decorator(func):
            if self._started:
                self.session.register(endpoint=func, procedure=procedure, options=options)
            else:

                def registerer():
                    self.session.register(endpoint=func, procedure=procedure, options=options)

                # Wait for the WAMP session to be started
                self._on_running_callbacks.append(registerer)
            return func

        return decorator

    def subscribe(self, topic, options=None):
        """Decorator for the :meth:`AutobahnSync.session.subscribe`

        .. note::
            This decorator can be used before :meth:`AutobahnSync.run` is called.
            In such case the actual registration will be done at ``run()`` time.
        """

        def decorator(func):
            if self._started:
                self.session.subscribe(handler=func, topic=topic, options=options)
            else:

                def subscriber():
                    self.session.subscribe(handler=func, topic=topic, options=options)

                # Wait for the WAMP session to be started
                self._on_running_callbacks.append(subscriber)
            return func

        return decorator
