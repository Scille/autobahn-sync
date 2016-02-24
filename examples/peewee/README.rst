Peewee app
==========

This example implement a simple app using sqlite and Peewee (don't forget to install it !)

The application is divided into two parts:
 - a backend ``library`` that expose wamp methods to create/retreive books
 - a frontend ``repl`` to communicate with the user

First start crossbar

    $ crossbar start

Then start the app in another terminal, given the backend part is already running
with crossbar, use ``--repl`` option to only run the terminal.

    $ python app.py --repl
    Welcome to the book shell, type `help` if you're lost
    > 
