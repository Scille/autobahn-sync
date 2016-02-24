from autobahn.wamp.exception import (
    Error, SessionNotReady, SerializationError, ProtocolError,
    TransportLost, ApplicationError, NotAuthorized, InvalidUri)  # noqa republishing
from twisted.internet.error import ConnectionRefusedError  # noqa republishing


__all__ = (
    'Error',
    'SessionNotReady',
    'SerializationError',
    'ProtocolError',
    'TransportLost',
    'ApplicationError',
    'NotAuthorized',
    'InvalidUri',

    'ConnectionRefusedError',

    'AbortError',
    'AlreadyRunningError',
    'NotRunningError'
)


class AbortError(Error):
    """
    Error raised when the soutes respond with an ABORT message to our HELLO
    """


class AlreadyRunningError(Error):
    """
    Error raised when trying to ``run()`` multiple time an :class:`autobahn_sync.AutobahnSync`
    """


class NotRunningError(Error):
    """
    Error raised when trying to ``stop()`` multiple time an :class:`autobahn_sync.AutobahnSync`
    """
