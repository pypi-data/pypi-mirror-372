"""
Composed indicator module.

This module defines composite indicators.
"""

__all__ = ["ContainerHealthIndicator", "CompositeHealthIndicator"]


from abc import ABC, abstractmethod
import asyncio
import logging

from .health import Health
from .indicator import HealthIndicator
from .status import Status


logger = logging.getLogger(__name__)


class ContainerHealthIndicator(HealthIndicator, ABC):
    """
    An abstract container health indicator that collects healths from its nested
    indicators returned by `get_component_indicators`.
    """

    __slots__ = ()

    async def get_health(self) -> Health:
        """
        Gets the health of the container.

        Returns:
            The summary health of the container and its nested components.
        """
        root_health = await self.get_root_health()
        component_health = await ContainerHealthIndicator.compose_health(self.get_component_indicators())

        if root_health:
            if not component_health:
                return root_health

            builder = Health.builder()
            builder.with_status(Status.revalidate(root_health.status, [component_health.status]))

            if root_health.details:
                builder.with_details(root_health.details)

            if root_health.components:
                builder.with_components(root_health.components)
            if component_health.components:
                builder.with_components(component_health.components)

            return builder.build()

        if component_health:
            return component_health

        return Health.builder().build()

    @abstractmethod
    async def get_root_health(self) -> Health | None:
        """Gets the health of the container itself.

        Returns:
            The own health.
        """

    @abstractmethod
    def get_component_indicators(self) -> list[HealthIndicator]:
        """Gets the list of component indicators.

        Returns:
            The list of nested indicators to collect healths from.
        """

    @staticmethod
    async def compose_health(indicators: list[HealthIndicator]) -> Health | None:
        """
        Compiles the summary health from a list of indicators.

        Args:
            indicators: The list of nested indicators to collect healths from.

        Returns:
            The summary health of the nested components.
        """
        builder = Health.builder()

        if not indicators:
            return None

        async def _collect(indicator: HealthIndicator) -> None:
            component: Health | None = None
            try:
                component = await indicator.get_health()
            except Exception as e:  # pylint: disable=broad-exception-caught
                my_type, my_name = type(indicator).__name__, indicator.get_name()
                logger.exception("Error calling %s.get_health() for %s: %s", my_type, my_name, e)
                component = Health.builder().with_exception(e).build()

            if component:
                builder.with_component(indicator.get_name(), component)

        await asyncio.gather(*[_collect(indicator) for indicator in indicators])
        return builder.build()


class CompositeHealthIndicator(ContainerHealthIndicator):
    """
    A container indicator with nested indicators specified in the constructor.
    This implementation does not have own health and returns `None` for the root health.
    """

    __slots__ = ("_name", "_indicators")

    def __init__(self, name: str, indicators: list[HealthIndicator]):
        """Initializes the composite health indicator.

        Args:
            name: The name of the indicator.
            indicators: The list of nested indicators to collect healths from.
        """
        self._name: str = name
        self._indicators: list[HealthIndicator] = indicators

    def get_name(self) -> str:
        """Returns the name of the indicator."""
        return self._name

    async def get_root_health(self) -> Health | None:
        """Returns the root health (absent for composite indicator)."""
        return None

    def get_component_indicators(self) -> list[HealthIndicator]:
        """Returns the list of nested indicators."""
        return self._indicators
