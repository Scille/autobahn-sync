import pytest

import sys
from twisted.python import log
log.startLogging(sys.stdout)


def pytest_addoption(parser):
    parser.addoption("--no-router", action='store_true',
                     help="Don't start WAMP router for the test"
                          " (must provide one on `ws://localhost:8080/ws` then)")
