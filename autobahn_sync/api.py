from .core import AutobahnSync
from .exceptions import NotRunningError


__all__ = (
    'app',
    'run',
    'register',
    'subscribe',
    'call',
    'publish',
    'on_challenge'
)


app = AutobahnSync()
run = app.run
register = app.register
subscribe = app.subscribe
on_challenge = app.on_challenge


def call(*args, **kwargs):
    if not app._started:
        raise NotRunningError("AutobahnSync not started, call `run` first")
    return app.session.call(*args, **kwargs)


def publish(*args, **kwargs):
    if not app._started:
        raise NotRunningError("AutobahnSync not started, call `run` first")
    return app.session.publish(*args, **kwargs)
