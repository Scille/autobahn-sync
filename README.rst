.. image:: https://travis-ci.org/Scille/autobahn-sync.svg?branch=master
    :target: https://travis-ci.org/Scille/autobahn-sync
    :alt: Travis-CI

.. image:: https://coveralls.io/repos/github/Scille/autobahn-sync/badge.svg?branch=master
    :target: https://coveralls.io/github/Scille/autobahn-sync?branch=master
    :alt: Code coverage

.. image:: https://readthedocs.org/projects/autobahn-sync/badge/?version=latest
    :target: http://autobahn-sync.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

Autobahn~Sync
=============

`Autobahn <http://autobahn.ws>`_ integration with `crochet <https://github.com/itamarst/crochet>`_ to provide WAMP for synchronous applications.

Originaly based on the work of `Sam & Max <http://sametmax.com/les-managers-le-detestent-faites-tourner-wamp-dans-django-avec-cette-astuce-insolite/>`_ (warning: French, pr0n and awesomeness inside !).

Quick example
-------------

.. code-block:: python

    from time import sleep
    from autobahn_sync import publish, call, register, subscribe, run


    @register('com.app.shout')
    def shout(msg):
        return msg.upper()


    @subscribe('com.app.idea')
    def on_thought(msg):
        print("I've just had a new idea: %s" % msg)


    run()
    while True:
        print(call('com.app.shout', 'Autobahn is cool !'))
        publish('com.app.idea', 'Use autobahn everywhere !')
        sleep(1)


This code will connect to the crossbar router (don't forget to start it
before trying this snippet !) listening ``ws://127.0.0.1:8080/ws``
and register itself in realm ``realm1``.

Also see the `examples <https://github.com/Scille/autobahn_sync/blob/master/examples>`_ for more usecases

Bonus
-----

See `extensions <https://github.com/Scille/autobahn_sync/tree/master/autobahn_sync/extensions>`_ folder for a nice Flask extension ;-)

Get it now
----------
::

   pip install -U autobahn-sync

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/Scille/autobahn_sync/blob/master/LICENSE>`_ file for more details.
