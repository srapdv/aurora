"""A set meta-classes that enforce states and behaviors on their children
Classes:
    DucListener
    CustomizationListener
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
    """Represents a listener for connected and removed DUCs"""

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


class CustomizationListener(ABC):
    """Represents a listener for the customization process of DUCs"""

    @abstractmethod
    def started(self, duc, customize_to):
        pass

    @abstractmethod
    def passed(self, duc, customize_to):
        pass

    @abstractmethod
    def failed(self, duc, customize_to):
        pass

    @abstractmethod
    def skipped(self, duc, customize_to):
        pass

    @abstractmethod
    def completed(self, duc, customize_to):
        pass
