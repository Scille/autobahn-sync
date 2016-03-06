import crochet
from autobahn.wamp import message, types
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet import defer, threads
from functools import partial

from .exceptions import AbortError
from .logger import logger


__all__ = ('_AsyncSession', 'SyncSession')


class _AsyncSession(ApplicationSession):
    """Custom :class:`autobahn.twisted.wamp.ApplicationSession` to get
    notified of ABORT messages
    """

    def __init__(self, config=None, join_config=None):
        super(_AsyncSession, self).__init__(config=config)
        self._join_config = join_config or {}
        self._sync_session = None
        self.on_join_defer = defer.Deferred()
        self.on_challenge_defer = defer.Deferred()

    def connect_to_sync(self, sync_session):
        self._sync_session = sync_session

    def onConnect(self):
        self.join(self.config.realm, **self._join_config)

    def onMessage(self, msg):
        if not self.is_attached():
            if isinstance(msg, message.Abort):
                logger.debug('Received ABORT answer to our HELLO: %s' % msg)
                details = types.CloseDetails(msg.reason, msg.message)
                self.on_join_defer.errback(AbortError(details))
            elif isinstance(msg, message.Welcome):
                logger.debug('Received WELCOME answer to our HELLO: %s' % msg)
                self.on_join_defer.callback(msg)
            else:
                logger.debug('Received: %s' % msg)
        return super(_AsyncSession, self).onMessage(msg)

    def onUserError(self, fail, msg):
        logger.error('%s\n%s' % (msg, fail.getTraceback()))
        super(_AsyncSession, self).onUserError(fail, msg)

    def onChallenge(self, challenge):
        logger.debug('Received CHALLENGE: %s' % challenge)
        # `sync_session._on_challenge` should resolve `self.on_challenge_defer`
        threads.deferToThread(partial(self._sync_session._on_challenge, challenge))
        return self.on_challenge_defer


class SyncSession(object):
    """Synchronous version of :class:`autobahn.twisted.wamp.ApplicationSession`
    """

    def __init__(self, callbacks_runner, on_challenge_callback):
        self._async_session = None
        self._callbacks_runner = callbacks_runner
        self._on_challenge_callback = on_challenge_callback

    def connect_to_async(self, async_session):
        self._async_session = async_session

    @crochet.wait_for(timeout=30)
    def leave(self, reason=None, message=None):
        """Actively close this WAMP session.

        Replace :meth:`autobahn.wamp.interface.IApplicationSession.leave`
        """
        # see https://github.com/crossbario/autobahn-python/issues/605
        return self._async_session.leave(reason=reason, log_message=message)

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

    @crochet.wait_for(timeout=30)
    def unsubscribe(self, subscription):
        return subscription.unsubscribe()

    def _on_challenge(self, challenge):
        # Function actually called by async_session to do the blocking onChallenge
        if not self._on_challenge_callback:
            self._async_session.on_challenge_defer.errback(
                NotImplementedError('No `on_challenge` callback provided'))
        try:
            ret = self._on_challenge_callback(challenge)
            self._async_session.on_challenge_defer.callback(ret)
        except Exception as e:
            self._async_session.on_challenge_defer.errback(e)
            self._async_session.on_join_defer.errback(AbortError(e))
