#! /bin/sh

PORT=8081 gunicorn "app:bootstrap()" -w 4
