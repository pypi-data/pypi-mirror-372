"""Health module.

This module contains the Health class, which is used to represent the health of a component.
"""

__all__ = ["Health", "HealthBuilder"]

from typing import Any, Self

from pydantic import BaseModel

from .status import Status


class Health(BaseModel):
    """A class that represents the health of a component."""

    status: Status | None = Status.UNKNOWN
    """The status of the component."""
    details: dict[str, Any] | None = None
    """The details of the component."""
    components: dict[str, Self] | None = None
    """The child components."""

    @staticmethod
    def builder(status: Status = Status.UNKNOWN) -> "HealthBuilder":
        """Creates a builder for building a Health object."""
        return HealthBuilder(status)


class HealthBuilder:
    """A builder for building Health objects."""

    def __init__(self, status: Status = Status.UNKNOWN):
        """
        Initializes a HealthBuilder object.

        Args:
            status: The initial status of the component.
        """
        self._status = status
        self._details: dict[str, Any] = {}
        self._components: dict[str, Health] = {}

    def with_status(self, status: Status) -> Self:
        """Sets the status."""
        self._status = status
        return self

    def with_detail(self, name: str, value: Any) -> Self:
        """Adds a detail."""
        self._details[name] = value
        return self

    def with_details(self, details: dict[str, Any]) -> Self:
        """Adds multiple details."""
        if details:
            self._details.update(details)
        return self

    def with_exception(self, exception: Exception) -> Self:
        """Adds information about an exception."""
        if exception:
            self._details["error"] = f"{exception.__class__.__name__}: {str(exception)}"
        return self

    def with_component(self, name: str, value: Health) -> Self:
        """Adds a child component."""
        self._components[name] = value
        return self

    def with_components(self, components: dict[str, Health]) -> Self:
        """Adds multiple child components."""
        if components:
            self._components.update(components)
        return self

    def build(self) -> Health:
        """Creates a Health object."""
        status = Status.revalidate(self._status, [component.status for component in self._components.values()])
        details = self._details if self._details else None
        components = self._components if self._components else None
        return Health(status=status, details=details, components=components)
