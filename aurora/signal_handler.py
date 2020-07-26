"""Intercepts and handles OS signals"""
import sys
import signal
import traceback


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
        print(
            f"KeyboardInterrupt (ID: {signum}) has been caught. Exiting Application..."
        )
        sys.exit(0)

    @classmethod
    def listen_for_sigint(cls):
        """Pauses the main thread while waiting for SIGINT"""
        signal.signal(signal.SIGINT, cls._handle_sigint)
        signal.pause()
