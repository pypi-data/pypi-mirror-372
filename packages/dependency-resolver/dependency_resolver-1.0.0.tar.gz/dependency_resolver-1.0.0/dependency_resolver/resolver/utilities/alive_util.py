import signal
import time
import logging

_logger:logging.Logger = logging.getLogger(__name__)  # module name

def keepAlive(sleep:int = 5) :
    """
    Keeps this python process alive by going into an infinite sleep-loop.
    This is useful for long-running processes that need to stay active.

    Args:
        sleep (int, optional): Number of seconds to sleep per loop. Defaults to 5.
    """
    _logger.debug("Going into an infinite loop...")
    while 1 :
        time.sleep(sleep)
    _logger.debug("...exiting loop.")


def setStopSignals(func) :
    """
    Sets up signal handlers for various shutdown signals.
    This function registers a given function to handle signals such as SIGTERM.
    When any of these signals are received, the specified function will be called.
    This is useful for gracefully shutting down a long-running process.

    Args:
        func (_type_): A function to call when a shutdown signal is received.
    """
    signal.signal(signal.SIGTERM, func)
    signal.signal(signal.SIGHUP, func)
    signal.signal(signal.SIGINT, func)
    signal.signal(signal.SIGUSR1, func)
    signal.signal(signal.SIGUSR2, func)
    signal.signal(signal.SIGQUIT, func)


def setChildStoppedSignal(func) :
    """
    Sets up a signal handler for when a child process has stopped.

    Args:
        func (_type_): A function to call when a child process stops.
    """
    signal.signal(signal.SIGCHLD, func)
