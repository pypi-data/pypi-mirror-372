"""Tests for the health module."""

from pygnosis import Health, HealthBuilder, Status


class TestHealth:
    """Tests for the Health class."""

    def test_health_default_values(self):
        """Test creating Health with default values."""
        health = Health()
        assert health.status == Status.UNKNOWN
        assert health.details is None
        assert health.components is None

    def test_health_with_status(self):
        """Test creating Health with specified status."""
        health = Health(status=Status.UP)
        assert health.status == Status.UP
        assert health.details is None
        assert health.components is None

    def test_health_with_details(self):
        """Test creating Health with details."""
        details = {"cpu": "90%", "memory": "50%"}
        health = Health(status=Status.UP, details=details)
        assert health.status == Status.UP
        assert health.details == details
        assert health.components is None

    def test_health_with_components(self):
        """Test creating Health with components."""
        component = Health(status=Status.DOWN)
        components = {"database": component}
        health = Health(status=Status.UP, components=components)
        assert health.status == Status.UP
        assert health.details is None
        assert health.components == components

    def test_health_with_all_fields(self):
        """Test creating Health with all fields populated."""
        details = {"version": "1.0.0"}
        component = Health(status=Status.UP)
        components = {"api": component}
        health = Health(status=Status.OUT_OF_SERVICE, details=details, components=components)
        assert health.status == Status.OUT_OF_SERVICE
        assert health.details == details
        assert health.components == components

    def test_health_builder_static_method(self):
        """Test the static builder method."""
        builder = Health.builder()
        assert isinstance(builder, HealthBuilder)

        health = builder.build()
        assert health.status == Status.UNKNOWN

    def test_health_builder_with_custom_status(self):
        """Test creating builder with custom status."""
        builder = Health.builder(Status.DOWN)
        assert isinstance(builder, HealthBuilder)

        health = builder.build()
        assert health.status == Status.DOWN


class TestHealthBuilder:
    """Tests for the HealthBuilder class."""

    def test_builder_init_default(self):
        """Test builder initialization with default values."""
        builder = HealthBuilder()
        health = builder.build()
        assert health.status == Status.UNKNOWN
        assert health.details is None
        assert health.components is None

    def test_builder_init_with_status(self):
        """Test builder initialization with specified status."""
        builder = HealthBuilder(Status.UP)
        health = builder.build()
        assert health.status == Status.UP
        assert health.details is None
        assert health.components is None

    def test_with_status(self):
        """Test the with_status method."""
        builder = HealthBuilder()
        result = builder.with_status(Status.DOWN)
        assert result is builder  # verify fluent interface
        health = builder.build()
        assert health.status == Status.DOWN

    def test_with_detail(self):
        """Test the with_detail method."""
        builder = HealthBuilder()
        result = builder.with_detail("key", "value")
        assert result is builder
        health = builder.build()
        assert health.details == {"key": "value"}

    def test_with_detail_multiple_calls(self):
        """Test multiple calls to with_detail method."""
        builder = HealthBuilder()
        builder.with_detail("key1", "value1").with_detail("key2", "value2")
        health = builder.build()
        assert health.details == {"key1": "value1", "key2": "value2"}

    def test_with_details_none(self):
        """Test with_details method with None input."""
        builder = HealthBuilder()
        result = builder.with_details(None)
        assert result is builder
        health = builder.build()
        assert health.details is None

    def test_with_details_empty_dict(self):
        """Test with_details method with empty dictionary."""
        builder = HealthBuilder()
        result = builder.with_details({})
        assert result is builder
        health = builder.build()
        assert health.details is None

    def test_with_details_valid_dict(self):
        """Test with_details method with valid dictionary."""
        builder = HealthBuilder()
        details = {"cpu": "80%", "memory": "60%"}
        result = builder.with_details(details)
        assert result is builder
        health = builder.build()
        assert health.details == details

    def test_with_details_updates_existing(self):
        """Test that with_details updates existing details."""
        builder = HealthBuilder()
        builder.with_detail("existing", "value")
        builder.with_details({"new": "value", "existing": "updated"})
        health = builder.build()
        assert health.details == {"existing": "updated", "new": "value"}

    def test_with_exception_none(self):
        """Test with_exception method with None input."""
        builder = HealthBuilder()
        result = builder.with_exception(None)
        assert result is builder
        health = builder.build()
        assert health.details is None

    def test_with_exception_valid(self):
        """Test with_exception method with valid exception."""
        builder = HealthBuilder()
        exception = ValueError("Test error")
        result = builder.with_exception(exception)
        assert result is builder
        health = builder.build()
        assert health.details == {"error": "ValueError: Test error"}

    def test_with_exception_preserves_other_details(self):
        """Test that with_exception preserves other details."""
        builder = HealthBuilder()
        builder.with_detail("other", "value")
        builder.with_exception(RuntimeError("Runtime error"))
        health = builder.build()
        assert health.details == {"other": "value", "error": "RuntimeError: Runtime error"}

    def test_with_component(self):
        """Test the with_component method."""
        builder = HealthBuilder()
        component = Health(status=Status.UP)
        result = builder.with_component("api", component)
        assert result is builder
        health = builder.build()
        assert health.components == {"api": component}

    def test_with_component_multiple_calls(self):
        """Test multiple calls to with_component method."""
        builder = HealthBuilder()
        comp1 = Health(status=Status.UP)
        comp2 = Health(status=Status.DOWN)
        builder.with_component("api", comp1).with_component("db", comp2)
        health = builder.build()
        assert health.components == {"api": comp1, "db": comp2}

    def test_with_components_none(self):
        """Test with_components method with None input."""
        builder = HealthBuilder()
        result = builder.with_components(None)
        assert result is builder
        health = builder.build()
        assert health.components is None

    def test_with_components_empty_dict(self):
        """Test with_components method with empty dictionary."""
        builder = HealthBuilder()
        result = builder.with_components({})
        assert result is builder
        health = builder.build()
        assert health.components is None

    def test_with_components_valid_dict(self):
        """Test with_components method with valid dictionary."""
        builder = HealthBuilder()
        comp1 = Health(status=Status.UP)
        comp2 = Health(status=Status.DOWN)
        components = {"api": comp1, "db": comp2}
        result = builder.with_components(components)
        assert result is builder
        health = builder.build()
        assert health.components == components

    def test_with_components_updates_existing(self):
        """Test that with_components updates existing components."""
        builder = HealthBuilder()
        existing_comp = Health(status=Status.UP)
        new_comp = Health(status=Status.DOWN)
        updated_comp = Health(status=Status.OUT_OF_SERVICE)

        builder.with_component("existing", existing_comp)
        builder.with_components({"new": new_comp, "existing": updated_comp})

        health = builder.build()
        assert health.components == {"existing": updated_comp, "new": new_comp}

    def test_build_empty_builder(self):
        """Test build method with empty builder."""
        builder = HealthBuilder()
        health = builder.build()
        assert health.status == Status.UNKNOWN
        assert health.details is None
        assert health.components is None

    def test_build_with_status_only(self):
        """Test build method with status only."""
        builder = HealthBuilder(Status.UP)
        health = builder.build()
        assert health.status == Status.UP
        assert health.details is None
        assert health.components is None

    def test_build_with_details_only(self):
        """Test build method with details only."""
        builder = HealthBuilder()
        builder.with_detail("key", "value")
        health = builder.build()
        assert health.status == Status.UNKNOWN
        assert health.details == {"key": "value"}
        assert health.components is None

    def test_build_with_components_revalidates_status(self):
        """Test that build method revalidates status based on components."""
        builder = HealthBuilder(Status.UP)
        down_component = Health(status=Status.DOWN)
        builder.with_component("service", down_component)

        health = builder.build()
        # Status.revalidate should return Status.DOWN because the component is DOWN
        assert health.status == Status.DOWN
        assert health.components == {"service": down_component}

    def test_build_details_none_when_empty(self):
        """Test that build returns None for details when dictionary is empty."""
        builder = HealthBuilder()
        health = builder.build()
        assert health.details is None

    def test_build_components_none_when_empty(self):
        """Test that build returns None for components when dictionary is empty."""
        builder = HealthBuilder()
        health = builder.build()
        assert health.components is None

    def test_fluent_interface_chain(self):
        """Test method chaining in fluent interface."""
        exception = ValueError("Test error")
        component = Health(status=Status.UP)

        health = (
            HealthBuilder(Status.DOWN)
            .with_detail("version", "1.0")
            .with_details({"build": "123"})
            .with_exception(exception)
            .with_component("api", component)
            .with_components({"cache": Health(status=Status.UP)})
            .build()
        )

        assert health.status == Status.DOWN  # should be revalidated based on components (DOWN wins)
        assert health.details == {"version": "1.0", "build": "123", "error": "ValueError: Test error"}

        # Components should be present
        assert health.components is not None
        assert len(health.components) == 2
        assert "api" in health.components
        assert "cache" in health.components
