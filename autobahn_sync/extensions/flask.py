from autobahn_sync import AutobahnSync, DEFAULT_AUTOBAHN_ROUTER, DEFAULT_AUTOBAHN_REALM


__all__ = ('FlaskAutobahnSync', )


class FlaskAutobahnSync(AutobahnSync):

    """Inherit from :class:`autobahn_sync.AutobahnSync` to integrate it with Flask.

    :param app: Flask app to configure, if provided :meth:`init_app` is automatically called
    :param config: remaining kwargs will be passed to ``init_app`` as configuration
    """

    def __init__(self, app=None, **config):
        super(FlaskAutobahnSync, self).__init__()
        self.config = {
            'router': DEFAULT_AUTOBAHN_ROUTER,
            'realm': DEFAULT_AUTOBAHN_REALM,
            'in_twisted': False
        }
        self.app = app
        if app is not None:
            self.init_app(app, **config)

    def init_app(self, app, router=None, realm=None, in_twisted=None):
        """Configure and call the :meth:`AutobahnSync.start` method

        :param app: Flask app to configure
        :param router: WAMP router to connect to
        :param realm: WAMP realm to connect to
        :param in_twisted: Is the code is going to run inside a Twisted application

        .. Note:: The config provided as argument will overwrite the one privided by ``app.config``
        """
        router = router or app.config.get('AUTHOBAHN_ROUTER')
        realm = realm or app.config.get('AUTHOBAHN_REALM')
        in_twisted = in_twisted or app.config.get('AUTHOBAHN_IN_TWISTED')
        if router:
            self.config['router'] = router
        if realm:
            self.config['realm'] = realm
        if in_twisted:
            self.run_in_twisted(url=self.config['router'], realm=self.config['realm'])
        else:
            self.run(url=self.config['router'], realm=self.config['realm'])
