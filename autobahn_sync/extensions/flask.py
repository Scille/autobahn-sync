from autobahn_sync import AutobahnSync, DEFAULT_AUTOBAHN_ROUTER, DEFAULT_AUTOBAHN_REALM


class FlaskAutobahnSync(object):

    def __init__(self, app=None, **config):
        self.config = {
            'router': DEFAULT_AUTOBAHN_ROUTER,
            'realm': DEFAULT_AUTOBAHN_REALM,
            'in_twisted': False
        }
        self.app = app
        self.autobahn_sync = AutobahnSync()
        if app is not None:
            self.init_app(app, **config)

    def init_app(self, app, router=None, realm=None, in_twisted=None):
        router = router or app.config.get('AUTHOBAHN_ROUTER')
        realm = realm or app.config.get('AUTHOBAHN_REALM')
        in_twisted = in_twisted or app.config.get('AUTHOBAHN_IN_TWISTED')
        if router:
            self.config['router'] = router
        if realm:
            self.config['realm'] = realm
        if in_twisted:
            self.config['in_twisted'] = in_twisted
        self.autobahn_sync.start(url=self.config['router'],
                                 realm=self.config['realm'],
                                 in_twisted=self.config['in_twisted'])

    def __getattr__(self, name):
        if name in ('publish', 'call', 'register', 'subscribe'):
            return getattr(self.autobahn_sync, name)
        else:
            super(FlaskAutobahnSync, self).__getattr__(self, name)
