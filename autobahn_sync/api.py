from .core import AutobahnSync


__all__ = (
    'app',
    'run',
    'register',
    'subscribe',
    'call',
    'publish',
)


app = AutobahnSync()
run = app.run
register = app.register
subscribe = app.subscribe

def call(*args, **kwargs):
    assert app.session
    return app.session.call(*args, **kwargs)

def publish(*args, **kwargs):
    assert app.session
    return app.session.publish(*args, **kwargs)
