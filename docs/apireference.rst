=============
API Reference
=============

Default API
-----------

Autobahn-Sync exposes an initialized :class:`autobahn_sync.AutobahnSync` at the
root of the module as a quick&easy access to the API::

    import autobahn_sync
    autobahn_sync.run(url=MY_ROUTER_URL, realm=MY_REALM)

    @autobahn_sync.subscribe('com.app.event')
    def on_event(e):
        print('%s happened' % e)

    autobahn_sync.publish('com.app.event', 'trigger !')


Advanced API
------------

With the need to connect to multiple realms/routers, the default API is not enought
and you should create other instances of :class:`autobahn_sync.AutobahnSync`.

.. automodule:: autobahn_sync
  :members:
  :undoc-members:


Flask extension
---------------

Flask extension provide an easier integration of Autobahn-Sync by doing it
configuration in three ways (by order of priority):
  - Configuration explicitly passed in ``init_app``
  - Configuration present in ``app.config``
  - Default configuration

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

================================= =========================================
Variable name                     Description
================================= =========================================
``AUTHOBAHN_ROUTER``              WAMP router to connect to (default: ``ws://localhost:8080/ws``)
``AUTHOBAHN_REALM``               WAMP realm to connect to (default: ``realm1``)
``AUTHOBAHN_IN_TWISTED``          Set to ``true`` if the code is going to run
                                  inside a Twisted application (default: ``false``)
================================= =========================================


.. automodule:: autobahn_sync.extensions.flask
    :members:
    :undoc-members:
