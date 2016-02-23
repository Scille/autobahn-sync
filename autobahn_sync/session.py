import crochet
from autobahn.wamp import message, types
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet import defer
from functools import partial

from .exceptions import AbortError
from .logger import logger


__all__ = ('AsyncSession', 'SyncSession')


class AsyncSession(ApplicationSession):
    """
    Custom ApplicationSession to get notified of ABORT message
    """

    def __init__(self, config=None):
        super(AsyncSession, self).__init__(config=config)
        self.on_join_defer = defer.Deferred()

    def onMessage(self, msg):
        if not self.is_attached():
            if isinstance(msg, message.Abort):
                logger.debug('Received ABORT answer to our HELLO: %s' % msg)
                details = types.CloseDetails(msg.reason, msg.message)
                self.on_join_defer.errback(AbortError(details))
            else:
                logger.debug('Received WELCOME answer to our HELLO: %s' % msg)
                self.on_join_defer.callback(msg)
        return super(AsyncSession, self).onMessage(msg)

    def onUserError(self, fail, msg):
        logger.error('%s\n%s' % (msg, fail.getTraceback()))
        super(AsyncSession, self).onUserError(fail, msg)


class SyncSession(object):
    """Synchronous subclass of :class:`autobahn.twisted.wamp._ApplicationSession`.
    """

    def __init__(self, async_session, callbacks_runner):
        self._async_session = async_session
        self._callbacks_runner = callbacks_runner

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

    @crochet.wait_for(timeout=30)
    def register(self, endpoint, procedure=None, options=None):
        """Register a procedure for remote calling.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.register`
        """
        def proxy_endpoint(*args, **kwargs):
            return self._callbacks_runner.put(partial(endpoint, *args, **kwargs))
        return self._async_session.register(proxy_endpoint, procedure=procedure, options=options)

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
        def proxy_handler(*args, **kwargs):
            return self._callbacks_runner.put(partial(handler, *args, **kwargs))
        return self._async_session.subscribe(proxy_handler, topic=topic, options=options)
