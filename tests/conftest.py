import pytest


def pytest_addoption(parser):
    parser.addoption("--no-router", action='store_true',
                     help="Don't start WAMP router for the test"
                          " (must provide one on `ws://localhost:8080/ws` then)")
    parser.addoption("--twisted-logs", action='store_true', help="Enable twisted logs output")


def pytest_runtest_setup(item):
    if item.config.getoption("--twisted-logs"):
        import sys
        from twisted.python import log
        log.startLogging(sys.stdout)
