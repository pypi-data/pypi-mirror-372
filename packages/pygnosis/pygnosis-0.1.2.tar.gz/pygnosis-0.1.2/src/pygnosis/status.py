"""Status module.

This module contains the Status class, which is used to represent the status of a component.
"""

__all__ = ["Status"]

from enum import Enum
from typing import Self


class Status(str, Enum):
    """A class that represents the status of a component."""

    UP = "UP"
    """The component is up and running."""
    DOWN = "DOWN"
    """The component is down and not running."""
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    """The component or some of its sub-components is not running properly."""
    UNKNOWN = "UNKNOWN"
    """The status of the component or some of its sub-components is unknown."""

    def __str__(self) -> str:
        """Returns the string representation of the status."""
        return self.value

    @staticmethod
    def of(value: bool | None) -> Self:
        """
        Returns a status based on a boolean value.

        Args:
            value: A boolean value.

        Returns:
            A Status.UNKNOWN if the value is None, Status.UP if the value is True, or Status.DOWN if the value is False.
        """
        if value is None:
            return Status.UNKNOWN

        return Status.UP if value else Status.DOWN

    @staticmethod
    def merge(status_list: list[Self]) -> Self | None:
        """
        Merges a list of statuses into a single resulting status.

        Args:
            status_list: A list of statuses.

        Returns:
            A Status.UNKNOWN if the list is empty, Status.UP if all statuses are Status.UP,
            Status.DOWN if all statuses are Status.DOWN, or Status.OUT_OF_SERVICE if any
            status is Status.UNKNOWN.
        """
        if not status_list:
            return None

        status_list = [status if status else Status.UNKNOWN for status in status_list]

        if all(status == Status.UP for status in status_list):
            return Status.UP

        if all(status == Status.DOWN for status in status_list):
            return Status.DOWN

        if any(status == Status.UNKNOWN for status in status_list):
            return Status.UNKNOWN

        return Status.OUT_OF_SERVICE

    @staticmethod
    def revalidate(initial_status: Self, status_list: list[Self]) -> Self:
        """
        Updates the component status based on the statuses of its child components.

        Args:
            initial_status: The initial status to revalidate.
            status_list: A list of statuses of the child components.

        Returns:
            The updated status of the component.
        """
        summary_status = Status.merge(status_list)
        if initial_status:
            if not summary_status:
                return initial_status

            if initial_status in [Status.UP, Status.UNKNOWN]:
                return summary_status

            return initial_status

        elif summary_status:
            return summary_status

        return Status.UNKNOWN
