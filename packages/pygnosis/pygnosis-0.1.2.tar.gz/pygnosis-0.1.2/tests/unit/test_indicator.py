"""Tests for the indicator module."""

from abc import ABC

import pytest

from pygnosis import Health, HealthIndicator, HealthIndicatorProvider, Status


class TestHealthIndicator:
    """Tests for the abstract HealthIndicator class."""

    def test_health_indicator_is_abstract(self):
        """Test that HealthIndicator is an abstract class."""
        assert issubclass(HealthIndicator, ABC)

        # Attempting to create an instance should raise TypeError
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            HealthIndicator()  # pylint: disable=abstract-class-instantiated

    def test_health_indicator_has_slots(self):
        """Test that HealthIndicator has empty slots."""
        assert hasattr(HealthIndicator, "__slots__")
        assert not HealthIndicator.__slots__

    def test_health_indicator_abstract_methods(self):
        """Test that HealthIndicator has the required abstract methods."""
        abstract_methods = HealthIndicator.__abstractmethods__
        assert "get_name" in abstract_methods
        assert "get_health" in abstract_methods


class TestHealthIndicatorProvider:
    """Tests for the abstract HealthIndicatorProvider class."""

    def test_health_indicator_provider_is_abstract(self):
        """Test that HealthIndicatorProvider is an abstract class."""
        assert issubclass(HealthIndicatorProvider, ABC)

        # Attempting to create an instance should raise TypeError
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            HealthIndicatorProvider()  # pylint: disable=abstract-class-instantiated

    def test_health_indicator_provider_has_slots(self):
        """Test that HealthIndicatorProvider has empty slots."""
        assert hasattr(HealthIndicatorProvider, "__slots__")
        assert not HealthIndicatorProvider.__slots__

    def test_health_indicator_provider_abstract_methods(self):
        """Test that HealthIndicatorProvider has the required abstract methods."""
        abstract_methods = HealthIndicatorProvider.__abstractmethods__
        assert "get_health_indicator" in abstract_methods


class MockHealthIndicator(HealthIndicator):
    """Mock implementation of HealthIndicator for testing."""

    def __init__(self, name: str, health: Health):
        self._name = name
        self._health = health

    def get_name(self) -> str:
        return self._name

    async def get_health(self) -> Health:
        return self._health


class MockHealthIndicatorProvider(HealthIndicatorProvider):
    """Mock implementation of HealthIndicatorProvider for testing."""

    def __init__(self, indicator: HealthIndicator):
        self._indicator = indicator

    def get_health_indicator(self) -> HealthIndicator:
        return self._indicator


class TestMockImplementations:
    """Tests for mock implementations of abstract classes."""

    def test_mock_health_indicator_get_name(self):
        """Test get_name method in mock implementation."""
        health = Health(status=Status.UP)
        indicator = MockHealthIndicator("test-service", health)
        assert indicator.get_name() == "test-service"

    @pytest.mark.asyncio
    async def test_mock_health_indicator_get_health(self):
        """Test get_health method in mock implementation."""
        health = Health(status=Status.DOWN, details={"error": "connection failed"})
        indicator = MockHealthIndicator("test-service", health)
        result = await indicator.get_health()
        assert result.status == Status.DOWN
        assert result.details == {"error": "connection failed"}

    def test_mock_health_indicator_provider_get_health_indicator(self):
        """Test get_health_indicator method in mock implementation."""
        health = Health(status=Status.UP)
        indicator = MockHealthIndicator("test-service", health)
        provider = MockHealthIndicatorProvider(indicator)
        result = provider.get_health_indicator()
        assert result is indicator
        assert result.get_name() == "test-service"

    @pytest.mark.asyncio
    async def test_integration_indicator_and_provider(self):
        """Integration test for indicator and provider interaction."""
        health = Health(status=Status.OUT_OF_SERVICE, details={"reason": "maintenance"})
        indicator = MockHealthIndicator("maintenance-service", health)
        provider = MockHealthIndicatorProvider(indicator)

        # Get indicator through provider
        retrieved_indicator = provider.get_health_indicator()
        assert retrieved_indicator.get_name() == "maintenance-service"

        # Get health through indicator
        retrieved_health = await retrieved_indicator.get_health()
        assert retrieved_health.status == Status.OUT_OF_SERVICE
        assert retrieved_health.details == {"reason": "maintenance"}
