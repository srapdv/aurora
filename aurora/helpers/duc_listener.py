"""A meta-class that enforces all its children to override its methods
Classes:
    DucListener
Misc Variables:
    __author__
    __copyright__
    __maintainer__
"""
__author__ = "Jego Carlo Ramos"
__copyright__ = "Copyright (C) 2020, Blackpearl Technology"
__maintainer__ = "Jego Carlo Ramos"

from abc import ABC, abstractmethod


class DucListener(ABC):
    """Represents a DUC listener"""

    @abstractmethod
    def add_duc(self, duc):
        """Runs when a DUC is added
        Parameters:
            duc (DUC) - The DUC to be handled
        """
        pass

    @abstractmethod
    def remove_duc(self, duc):
        """Runs when a DUC is removed
        Paramaters:
            duc (DUC) - The DUC to be handled
        """
        pass