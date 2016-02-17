import crochet
from autobahn.twisted.wamp import Application


DEFAULT_AUTOBAHN_ROUTER = u"ws://127.0.0.1:8080/ws"
DEFAULT_AUTOBAHN_REALM = u"realm1"
crochet_initialized = False


def init_crochet(in_twisted=False):
    global crochet_initialized
    if crochet_initialized:
        return
    if in_twisted:
        crochet.no_setup()
    else:
        crochet.setup()
    crochet_initialized = True


class AutobahnSync(object):
    def __init__(self):
        self.wapp = Application()

    @crochet.wait_for(timeout=30)
    def publish(self, topic, *args, **kwargs):
        return self.wapp.session.publish(topic, *args, **kwargs)

    @crochet.wait_for(timeout=30)
    def call(self, name, *args, **kwargs):
        return self.wapp.session.call(name, *args, **kwargs)

    def register(self, name, *args, **kwargs):
        @crochet.run_in_reactor
        def decorator(func):
            self.wapp.register(name, *args, **kwargs)(func)
        return decorator

    def subscribe(self, name, *args, **kwargs):
        @crochet.run_in_reactor
        def decorator(func):
            self.wapp.subscribe(name, *args, **kwargs)(func)
        return decorator

    def start(self, url=DEFAULT_AUTOBAHN_ROUTER, realm=DEFAULT_AUTOBAHN_REALM,
              in_twisted=False, **kwargs):
        init_crochet(in_twisted=in_twisted)

        class ErrorCollector(object):
            exception = None

            def __call__(self, failure):
                self.exception = failure.value

        connect_error = ErrorCollector()

        @crochet.wait_for(timeout=30)
        def _starter():
            d = self.wapp.run(url=url, realm=realm, start_reactor=False, **kwargs)
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
