Flask extension
---------------

Example make use of the flask extension to automatically configure Autobahn-Sync according to the app's config.


First start crossbar

```sh
$ crossbar start
```

> **Note**
crossbar configuration use "reverseproxy" option which is only available
in crossbar>v0.12.1, with lower version you can remove this configuration and
use http://localhost:8081/ to access the example


Then launch the app, to do so you have the choice between "dev mode":

```sh
$ python app.py
 * Running on http://127.0.0.1:8081/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger pin code: 230-774-136
```

> **Note:**
Given Autobahn-Sync makes use of threads, flask's autoreload function
is kind of buggy and should not be used (yeah, that sucks...)


or "production mode" with Gunicorn running the app on 4 concurrent workers:

```sh
$ ./runserver.sh
[2016-02-24 11:28:27 +0000] [12770] [INFO] Starting gunicorn 19.4.5
[2016-02-24 11:28:27 +0000] [12770] [INFO] Listening at: http://0.0.0.0:8081 (12770)
[2016-02-24 11:28:27 +0000] [12770] [INFO] Using worker: sync
[2016-02-24 11:28:27 +0000] [12775] [INFO] Booting worker with pid: 12775
[2016-02-24 11:28:28 +0000] [12776] [INFO] Booting worker with pid: 12776
[2016-02-24 11:28:28 +0000] [12784] [INFO] Booting worker with pid: 12784
[2016-02-24 11:28:28 +0000] [12789] [INFO] Booting worker with pid: 12789
```

Now you can head to http://localhost:8080/ and see the request history change
each time you hit reload !
