import crochet
from autobahn.twisted.wamp import Application, ApplicationRunner


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
    """AutobahnSync main class, wrapp the ``Autobahn`` api within ``crochet``
    to turn it synchronous
    """
    def __init__(self):
        self.wapp = Application()
        self._started = False

    @crochet.wait_for(timeout=30)
    def publish(self, topic, *args, **kwargs):
        """Publish an event to a topic.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.publish`
        """
        return self.wapp.session.publish(topic, *args, **kwargs)

    @crochet.wait_for(timeout=30)
    def call(self, name, *args, **kwargs):
        """Call a remote procedure.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.call`
        """
        return self.wapp.session.call(name, *args, **kwargs)

    def register(self, name, *args, **kwargs):
        """Decorator exposing a function as a remote callable procedure.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.register`
        """

        @crochet.run_in_reactor
        def decorator(func):
            self.wapp.register(name, *args, **kwargs)(func)
        return decorator

    def subscribe(self, name, *args, **kwargs):
        """Decorator attaching a function as an event handler.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.subscribe`
        """
        @crochet.run_in_reactor
        def decorator(func):
            self.wapp.subscribe(name, *args, **kwargs)(func)
        return decorator

    def start(self, url=DEFAULT_AUTOBAHN_ROUTER, realm=DEFAULT_AUTOBAHN_REALM,
              in_twisted=False, **kwargs):
        """Start the background twisted thread and create the wamp connection

        .. note:: This function must be called first
        """
        if self._started:
            raise RuntimeError("This AutobahnSync instance is already started")
        _init_crochet(in_twisted=in_twisted)

        if in_twisted:
            self._in_twisted_start(url=url, realm=realm, **kwargs)
        else:
            self._out_twisted_start(url=url, realm=realm, **kwargs)
        self._started = True

    def _in_twisted_start(self, **kwargs):

        class ErrorCollector(object):
            def __call__(self, failure):
                raise failure.value

        connect_error = ErrorCollector()

        runner = ApplicationRunner(**kwargs)
        d = runner.run(self.wapp.__call__, start_reactor=False)
        d.addErrback(connect_error)

    def _out_twisted_start(self, **kwargs):

        class ErrorCollector(object):
            exception = None

            def __call__(self, failure):
                self.exception = failure.value

        connect_error = ErrorCollector()

        @crochet.wait_for(timeout=30)
        def _starter():
            runner = ApplicationRunner(**kwargs)
            d = runner.run(self.wapp.__call__, start_reactor=False)
            d.addErrback(connect_error)
            return d

        _starter()
        if connect_error.exception:
            raise connect_error.exception


default_app = AutobahnSync()
publish = default_app.publish
call = default_app.call
register = default_app.register
subscribe = default_app.subscribe
start = default_app.start
