from uuid import uuid4
from flask import Flask
from datetime import datetime
from autobahn_sync.extensions.flask import FlaskAutobahnSync
from autobahn.wamp import PublishOptions


worker_id = uuid4().hex
app = Flask(__name__)
serve_history = []


def bootstrap():
    wamp = FlaskAutobahnSync(app)
    app.wamp = wamp

    @wamp.subscribe('com.flask_app.page_served')
    def page_served(wid, timestamp):
        data = (wid, timestamp)
        print('[Worker %s] Received %s' % (worker_id, data))
        serve_history.append(data)

    return app


@app.route('/')
def main():
    timestamp = str(datetime.utcnow())
    print('[Worker %s] Serve request on timestamp %s' % (worker_id, timestamp))
    publish_opt = PublishOptions(exclude_me=False)
    app.wamp.session.publish('com.flask_app.page_served', worker_id,
                             timestamp, options=publish_opt)
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
    app.run(port=8081)
