"""A contract that all DUC listeners must adhere to"""
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
