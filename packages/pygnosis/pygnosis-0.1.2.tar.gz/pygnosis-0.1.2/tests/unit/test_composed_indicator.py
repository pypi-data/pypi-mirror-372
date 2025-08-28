"""Tests for the composed_indicator module."""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from pygnosis import (
    CompositeHealthIndicator,
    ContainerHealthIndicator,
    Health,
    HealthIndicator,
    Status,
)


class MockHealthIndicator(HealthIndicator):
    """Mock implementation of HealthIndicator for testing."""

    def __init__(self, name: str, health: Health | None = None, exception: Exception | None = None):
        self._name = name
        self._health = health
        self._exception = exception

    def get_name(self) -> str:
        return self._name

    async def get_health(self) -> Health:
        if self._exception:
            raise self._exception
        return self._health


class MockContainerHealthIndicator(ContainerHealthIndicator):
    """Mock implementation of ContainerHealthIndicator for testing."""

    def __init__(self, name: str, root_health: Health | None = None, indicators: list[HealthIndicator] | None = None):
        self._name = name
        self._root_health = root_health
        self._indicators = indicators or []

    def get_name(self) -> str:
        return self._name

    async def get_root_health(self) -> Health | None:
        return self._root_health

    def get_component_indicators(self) -> list[HealthIndicator]:
        return self._indicators


class TestContainerHealthIndicator:
    """Tests for the abstract ContainerHealthIndicator class."""

    @pytest.mark.asyncio
    async def test_get_health_no_root_no_components(self):
        """Test get_health with no root health and no components."""
        container = MockContainerHealthIndicator("test", root_health=None, indicators=[])
        health = await container.get_health()

        assert health.status == Status.UNKNOWN
        assert health.details is None
        assert health.components is None

    @pytest.mark.asyncio
    async def test_get_health_only_root_health(self):
        """Test get_health with only root health."""
        root_health = Health(status=Status.UP, details={"version": "1.0"})
        container = MockContainerHealthIndicator("test", root_health=root_health, indicators=[])
        health = await container.get_health()

        assert health.status == Status.UP
        assert health.details == {"version": "1.0"}
        assert health.components is None

    @pytest.mark.asyncio
    async def test_get_health_only_component_health(self):
        """Test get_health with only component health."""
        indicator = MockHealthIndicator("api", Health(status=Status.DOWN))
        container = MockContainerHealthIndicator("test", root_health=None, indicators=[indicator])
        health = await container.get_health()

        assert health.status == Status.DOWN
        assert health.components is not None
        assert "api" in health.components

    @pytest.mark.asyncio
    async def test_get_health_merge_root_has_components(self):
        """Test get_health with both root health and components, root has components."""
        container = MockContainerHealthIndicator(
            "test",
            root_health=Health(
                status=Status.UP, details={"root": "info"}, components={"sub-root": Health(status=Status.UP)}
            ),
            indicators=[MockHealthIndicator("api", Health(status=Status.UP, details={"api": "info"}))],
        )
        health = await container.get_health()

        # Status should be revalidated
        assert health.status == Status.UP

        # Details should be combined - verify they exist
        assert health.details is not None
        assert "root" in health.details
        assert health.details["root"] == "info"

        # Components should be present
        assert health.components is not None
        assert len(health.components) == 2
        assert "api" in health.components
        assert "sub-root" in health.components

    @pytest.mark.asyncio
    async def test_get_health_merge_component_returns_none(self):
        """Test get_health with both root health and components, component return None."""
        container = MockContainerHealthIndicator(
            "test",
            root_health=Health(status=Status.DOWN, details={"root": "info"}),
            indicators=[MockHealthIndicator(name="api")],
        )
        health = await container.get_health()

        # Status should be revalidated
        assert health.status == Status.DOWN

        # Details should be combined - verify they exist
        assert health.details is not None
        assert "root" in health.details
        assert health.details["root"] == "info"

        # Components should be present
        assert health.components is None

    # @pytest.mark.asyncio
    # async def test_get_health_merge_both_has_components(self):
    #     """Test get_health with both root health and components, root and component has sub-components."""
    #     container = MockContainerHealthIndicator(
    #         "test",
    #         root_health=Health(
    #             status=Status.DOWN,
    #             details={"root": "info"},
    #             components={"sub-root": Health(status=Status.UP)},
    #         ),
    #         indicators=[
    #             MockHealthIndicator(
    #                 "api",
    #                 Health(
    #                     status=Status.UP,
    #                     details={"api": "info"},
    #                     components={"sub-api": Health(status=Status.UP)},
    #                 ),
    #             )
    #         ],
    #     )
    #     health = await container.get_health()

    #     # Status should be revalidated
    #     assert health.status == Status.DOWN

    #     # Details should be combined - verify they exist
    #     assert health.details is not None
    #     assert "root" in health.details
    #     assert health.details["root"] == "info"

    #     # Components should be present
    #     assert health.components is not None
    #     assert len(health.components) == 3
    #     assert "sub-root" in health.components
    #     assert "api" in health.components
    #     assert "sub-api" in health.components

    @pytest.mark.asyncio
    async def test_get_health_status_revalidation(self):
        """Test status revalidation between root and component health."""
        root_health = Health(status=Status.UP)
        down_indicator = MockHealthIndicator("failing-service", Health(status=Status.DOWN))
        container = MockContainerHealthIndicator("test", root_health=root_health, indicators=[down_indicator])
        health = await container.get_health()

        # Status should be DOWN due to failing component
        assert health.status == Status.DOWN

    @pytest.mark.asyncio
    async def test_compose_health_empty_indicators(self):
        """Test compose_health with empty list of indicators."""
        result = await ContainerHealthIndicator.compose_health([])
        assert result is None

    @pytest.mark.asyncio
    async def test_compose_health_single_indicator(self):
        """Test compose_health with a single indicator."""
        indicator = MockHealthIndicator("service", Health(status=Status.UP, details={"test": "value"}))
        result = await ContainerHealthIndicator.compose_health([indicator])

        assert result.status == Status.UP
        assert result.components is not None
        assert "service" in result.components
        assert result.components["service"].details == {"test": "value"}

    @pytest.mark.asyncio
    async def test_compose_health_multiple_indicators(self):
        """Test compose_health with multiple indicators."""
        indicators = [
            MockHealthIndicator("api", Health(status=Status.UP)),
            MockHealthIndicator("db", Health(status=Status.UP)),
            MockHealthIndicator("cache", Health(status=Status.DOWN)),
        ]
        result = await ContainerHealthIndicator.compose_health(indicators)

        # Status should be OUT_OF_SERVICE (UP + DOWN mix)
        assert result.status == Status.OUT_OF_SERVICE
        assert result.components is not None
        assert len(result.components) == 3
        assert "api" in result.components
        assert "db" in result.components
        assert "cache" in result.components

    @pytest.mark.asyncio
    async def test_compose_health_with_exception(self):
        """Test compose_health with exception in indicator."""
        exception = RuntimeError("Service unavailable")
        indicators = [
            MockHealthIndicator("working-service", Health(status=Status.UP)),
            MockHealthIndicator("failing-service", exception=exception),
        ]
        result = await ContainerHealthIndicator.compose_health(indicators)

        # Verify result - UNKNOWN because there is an exception
        assert result.status == Status.UNKNOWN
        assert result.components is not None
        assert len(result.components) == 2
        assert "working-service" in result.components
        assert "failing-service" in result.components

        # Failing service should contain error information
        failing_component = result.components.get("failing-service")
        assert failing_component is not None
        assert failing_component.details is not None
        assert "error" in failing_component.details
        assert "RuntimeError: Service unavailable" in failing_component.details["error"]

    @pytest.mark.asyncio
    async def test_compose_health_all_exceptions(self):
        """Test compose_health when all indicators throw exceptions."""
        indicators = [
            MockHealthIndicator("service1", exception=ValueError("Error 1")),
            MockHealthIndicator("service2", exception=ConnectionError("Error 2")),
        ]
        result = await ContainerHealthIndicator.compose_health(indicators)

        assert result.status == Status.UNKNOWN
        assert result.components is not None
        assert len(result.components) == 2

        # All components should contain error information
        for component in result.components.values():
            assert component.details is not None
            assert "error" in component.details


class TestCompositeHealthIndicator:
    """Tests for the CompositeHealthIndicator class."""

    def test_composite_health_indicator_init(self):
        """Test CompositeHealthIndicator initialization."""
        indicators = [MockHealthIndicator("service1"), MockHealthIndicator("service2")]
        composite = CompositeHealthIndicator("test-composite", indicators)

        assert composite.get_name() == "test-composite"
        assert composite.get_component_indicators() == indicators

    def test_get_name(self):
        """Test the get_name method."""
        composite = CompositeHealthIndicator("my-composite", [])
        assert composite.get_name() == "my-composite"

    @pytest.mark.asyncio
    async def test_get_root_health_returns_none(self):
        """Test that get_root_health returns None."""
        composite = CompositeHealthIndicator("test", [])
        result = await composite.get_root_health()
        assert result is None

    def test_get_component_indicators(self):
        """Test the get_component_indicators method."""
        indicators = [MockHealthIndicator("service1"), MockHealthIndicator("service2")]
        composite = CompositeHealthIndicator("test", indicators)
        result = composite.get_component_indicators()
        assert result == indicators

    @pytest.mark.asyncio
    async def test_get_health_empty_indicators(self):
        """Test get_health with empty list of indicators."""
        composite = CompositeHealthIndicator("empty", [])
        health = await composite.get_health()

        assert health.status == Status.UNKNOWN
        assert health.details is None
        assert health.components is None

    @pytest.mark.asyncio
    async def test_get_health_with_indicators(self):
        """Test get_health with indicators."""
        indicators = [
            MockHealthIndicator("api", Health(status=Status.UP)),
            MockHealthIndicator("db", Health(status=Status.DOWN)),
        ]
        composite = CompositeHealthIndicator("services", indicators)
        health = await composite.get_health()

        assert health.status == Status.OUT_OF_SERVICE  # UP + DOWN
        assert health.components is not None
        assert len(health.components) == 2
        assert "api" in health.components
        assert "db" in health.components


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_compose_health_with_none_health(self):
        """Test compose_health with indicator returning None."""
        # Create indicator using AsyncMock to return None
        mock_indicator = Mock(spec=HealthIndicator)
        mock_indicator.get_name.return_value = "null-service"
        mock_indicator.get_health = AsyncMock(return_value=None)

        result = await ContainerHealthIndicator.compose_health([mock_indicator])

        # If indicator returns None, component should not be added
        assert result.status == Status.UNKNOWN
        assert result.components is None or len(result.components) == 0

    @pytest.mark.asyncio
    async def test_get_health_with_none_values_in_details(self):
        """Test merging details with None values."""
        root_health = Health(status=Status.UP, details={"key1": None, "key2": "value"})
        indicator = MockHealthIndicator("service", Health(status=Status.UP, details={"key3": None}))
        container = MockContainerHealthIndicator("test", root_health=root_health, indicators=[indicator])
        health = await container.get_health()

        assert health.details is not None
        assert "key1" in health.details
        assert health.details["key1"] is None
        assert health.details["key2"] == "value"

        # key3 is in components, not in main details
        assert health.components is not None
        assert "service" in health.components
        assert health.components["service"].details is not None
        assert "key3" in health.components["service"].details

    @pytest.mark.asyncio
    async def test_get_health_with_none_components(self):
        """Test merging components with None values."""
        # This test checks behavior when root_health.components or component_health.components is None
        root_health = Health(status=Status.UP, components=None)
        indicator = MockHealthIndicator("service", Health(status=Status.UP))
        container = MockContainerHealthIndicator("test", root_health=root_health, indicators=[indicator])
        health = await container.get_health()

        # Should get components only from compose_health
        assert health.components is not None
        assert "service" in health.components

    @pytest.mark.asyncio
    async def test_timeout_behavior(self):
        """Test that tests complete within timeout limits."""
        # Create indicator that "hangs"
        mock_indicator = Mock(spec=HealthIndicator)
        mock_indicator.get_name.return_value = "slow-service"

        async def slow_get_health():
            await asyncio.sleep(10)  # Longer than test timeout
            return Health(status=Status.UP)

        mock_indicator.get_health = slow_get_health

        # Test should timeout (5 seconds) before sleep(10) completes
        with pytest.raises(asyncio.TimeoutError):
            async with asyncio.timeout(1):  # Even shorter timeout for this specific test
                await ContainerHealthIndicator.compose_health([mock_indicator])
