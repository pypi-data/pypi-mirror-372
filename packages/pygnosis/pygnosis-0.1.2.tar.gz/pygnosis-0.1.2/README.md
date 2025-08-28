# Pygnosis

Asynchronous health checks for Python services.

![CI](https://github.com/javamaker-python/pygnosis/actions/workflows/ci.yml/badge.svg?branch=main)
[![codecov](https://codecov.io/gh/javamaker-python/pygnosis/branch/main/graph/badge.svg)](https://codecov.io/gh/javamaker-python/pygnosis)

Features
--------

- Flexible health indicators (define your own checks)
- Composable architecture (nest indicators into trees)
- Full async/await support
- Type hints throughout
- Graceful error handling

Installation
------------

```bash
pip install pygnosis
```

Quick start
-----------

```python
import asyncio
from pygnosis import Health, HealthIndicator, Status, CompositeHealthIndicator


class DatabaseHealthIndicator(HealthIndicator):
    def get_name(self) -> str:
        return "database"

    async def get_health(self) -> Health:
        try:
            return Health.builder(Status.UP).with_detail("connections", 10).build()
        except Exception as e:
            return Health.builder(Status.DOWN).with_exception(e).build()


class RedisHealthIndicator(HealthIndicator):
    def get_name(self) -> str:
        return "redis"

    async def get_health(self) -> Health:
        return Health.builder(Status.UP).build()


async def main():
    composite = CompositeHealthIndicator(
        name="app",
        indicators=[DatabaseHealthIndicator(), RedisHealthIndicator()],
    )
    health = await composite.get_health()
    print(f"Status: {health.status}")
    print(f"Components: {health.components}")


if __name__ == "__main__":
    asyncio.run(main())
```

Development with uv
-------------------

```bash
uv sync --group dev
uv run ruff check src/ tests/
uv run pytest
```

Building the package
--------------------

```bash
uv build
```

Documentation
-------------

Sphinx docs are built in CI. Locally:

```bash
uv sync --group docs
uv run sphinx-build -b html docs docs/_build/html
```

License
-------

MIT License — see [LICENSE](LICENSE)

Contributing
------------

Contributions are welcome. See `CONTRIBUTING.md` for guidelines.