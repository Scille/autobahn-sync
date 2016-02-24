import os
from flask import Flask
from datetime import datetime
from autobahn_sync.extensions.flask import FlaskAutobahnSync
from autobahn.wamp import PublishOptions, RegisterOptions


worker_id = os.getpid()
app = Flask(__name__)


def bootstrap():
    wamp = FlaskAutobahnSync(app)
    app.wamp = wamp
    serve_history = []

    @wamp.subscribe(u'com.flask_app.page_served')
    def page_served(wid, timestamp):
        data = (wid, timestamp)
        print('[Worker %s] Received %s' % (worker_id, data))
        serve_history.append(data)

    # Authorize multiple registers given we can start this app in concurrent workers
    register_opt = RegisterOptions(invoke=u'random')
    @wamp.register(u'com.flask_app.get_request_history', options=register_opt)
    def get_request_history(wid):
        print('[Worker %s] Send request history to worker %s' % (worker_id, wid))
        return serve_history

    return app


@app.route('/')
def main():
    timestamp = str(datetime.utcnow())
    print('[Worker %s] Serve request on timestamp %s' % (worker_id, timestamp))
    publish_opt = PublishOptions(exclude_me=False)
    app.wamp.session.publish('com.flask_app.page_served', worker_id,
                             timestamp, options=publish_opt)
    serve_history = app.wamp.session.call(
        'com.flask_app.get_request_history', worker_id)
    txts = [
        "<table>",
        "<thead><th>Worker id</th><th>Request timestamp</th></thead>",
        "<tbody>"
    ]
    txts += ["<tr><td>%s</td><td>%s</td></tr>" % (wid, ts)
             for wid, ts in serve_history]
    txts.append("</tbody></table>")
    return ''.join(txts)


if __name__ == '__main__':
    bootstrap()
    app.run(port=8081, debug=True)
