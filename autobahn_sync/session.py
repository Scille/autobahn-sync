import crochet
from autobahn.wamp import message, types
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet import defer

from .exceptions import AbortError


class AsyncSession(ApplicationSession):
    """
    Custom ApplicationSession to get notified of ABORT message
    """

    def __init__(self, config=None):
        super(AsyncSession, self).__init__(config=config)
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
        return super(AsyncSession, self).onMessage(msg)


class SyncSession(object):
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
