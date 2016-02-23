import crochet
from threading import Thread
from twisted.internet import reactor, defer

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


__all__ = ('CallbacksRunner', 'ThreadedCallbacksRunner')


class CallbacksRunner(object):
    def __init__(self):
        self._started = False
        self._callbacks = Queue()

    def put(self, func):
        answer = defer.Deferred()
        self._callbacks.put((func, answer))
        return answer

    def start(self):
        assert not self._started, 'Already started !'
        self._started = True
        while self._started:
            # Get back and execute requested callbacks
            func, answer = self._callbacks.get()
            try:
                reactor.callFromThread(answer.callback, func())
            except Exception as e:
                reactor.callFromThread(answer.errback, e)

    def stop(self):
        self._started = False
        # Add dummy function to force queue wakeup
        self.put(lambda: None)


class ThreadedCallbacksRunner(CallbacksRunner):
    def __init__(self):
        super(ThreadedCallbacksRunner, self).__init__()
        self._thread = None

    def start(self):
        # TODO: use twisted threadspool ?
        self._thread = Thread(target=super(ThreadedCallbacksRunner, self).start)
        self._thread.start()
        # Kill this thread once main have left
        crochet.register(self.stop)
