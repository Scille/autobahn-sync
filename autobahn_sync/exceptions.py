from autobahn.wamp.exception import *  # noqa republishing
from twisted.internet.error import ConnectionRefusedError  # noqa republishing


class AbortError(Error):
    """
    Error raised when the soutes respond with an ABORT message to our HELLO
    """


class AlreadyRunningError(Error):
    """
    Error raised when trying to ``run()`` multiple time an :class:`autobahn_sync.AutobahnSync`
    """
