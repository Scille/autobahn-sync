#! /usr/bin/env python3

from datetime import datetime
from os import environ

from flask import Flask
from autobahn_sync.extensions.flask import FlaskAutobahnSync


app = Flask(__name__)
app.config['AUTHOBAHN_IN_TWISTED'] = environ.get('AUTHOBAHN_IN_TWISTED', '').lower() == 'true'
wamp_default = FlaskAutobahnSync(app)
wamp_realm2 = FlaskAutobahnSync(app, realm=u'realm2')


@wamp_default.register('com.realm1.action')
def _():
    print('Got RPC on com.realm1.action')
    return 'realm1 %s' % datetime.utcnow()


@wamp_realm2.register('com.realm2.action')
def _():
    print('Got RPC on com.realm2.action')
    return 'realm2 %s' % datetime.utcnow()


@app.route('/')
def main():
    print('RPC on realm1')
    ts1 = wamp_default.call('com.realm1.action')
    print('com.realm1.action returned %s' % ts1)
    print('RPC on realm2')
    ts2 = wamp_realm2.call('com.realm2.action')
    print('com.realm2.action returned %s' % ts2)
    return "realm1 RPC: %s<br><br>realm2 RPC: %s" % (ts1, ts2)


if __name__ == '__main__':
    app.run(port=int(environ.get('PORT', 8080)), debug=False)
