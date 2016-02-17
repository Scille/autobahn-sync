#! /usr/bin/env python3

from datetime import datetime
from os import environ

from flask import Flask
from autobahn_sync.extensions.flask import FlaskAutobahnSync


app = Flask(__name__)
app.config['AUTHOBAHN_IN_TWISTED'] = environ.get('AUTHOBAHN_IN_TWISTED', '').lower() == 'true'
wamp = FlaskAutobahnSync(app)


@wamp.register('com.clock.get_timestamp')
def get_timestamp():
    print('Got RPC on get_timestamp')
    return str(datetime.utcnow())


@app.route('/')
def main():
    wamp.publish('com.clock.connection')
    print('Send RPC on get_timestamp')
    ts = wamp.call('com.clock.get_timestamp')
    return 'Now is %s' % ts


@wamp.subscribe('com.clock.connection')
def tick_listener(tick):
    print('Received com.clock.connection')


if __name__ == '__main__':
    app.run(port=int(environ.get('PORT', 8081)), debug=True)
