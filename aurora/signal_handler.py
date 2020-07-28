"""Intercepts and handles OS signals

Classes:
    SignalHandler
Misc Variables:
    __author__
    __copyright__
    __maintainer__
    logger_builder
    logger
"""
import sys
import signal
import traceback
from helpers.logger import LoggerBuilder

log_builder = LoggerBuilder("stonehenge", __name__)
logger = log_builder.create_logger()


class SignalHandler:
    """Represents a Signal handler"""

    @classmethod
    def _handle_sigint(cls, signum, frame):
        """Responses to the program interrupt signal
        Parameter:
            signum (int) - The integer representation of SIGINT
            frame - The stack frame. This parameter is required because any thread might
                    be interrupted by a signal, but the signal is only received in the
                    main thread
        """
        logger.info(
            f"KeyboardInterrupt (ID: {signum}) has been caught. Exiting Application..."
        )
        sys.exit(0)

    @classmethod
    def listen_for_sigint(cls):
        """Pauses the main thread while waiting for SIGINT"""
        signal.signal(signal.SIGINT, cls._handle_sigint)
        signal.pause()


if __name__ == "__main__":
    SignalHandler.listen_for_sigint()
