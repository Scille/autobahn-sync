import logging
logger = logging.getLogger('autobahn')

# Time to debug ? Uncomment this !
# logger.setLevel(logging.DEBUG)
# steam_handler = logging.StreamHandler()
# steam_handler.setLevel(logging.DEBUG)
# logger.addHandler(steam_handler)

# Need twisted logs ?
# import sys
# from twisted.python import log
# log.startLogging(sys.stdout)


__all__ = ('logger', )
