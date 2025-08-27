Shadow is a distributed background task system for Python functions with a focus
on the scheduling of future work as seamlessly and efficiently as immediate work.

[![PyPI - Version](https://img.shields.io/pypi/v/shadows)](https://pypi.org/project/shadows/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/shadows)](https://pypi.org/project/shadows/)
[![GitHub main checks](https://img.shields.io/github/check-runs/SRSWTI/shadows/main)](https://github.com/SRSWTI/shadows/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/SRSWTI/shadows)](https://app.codecov.io/gh/SRSWTI/shadows)
[![PyPI - License](https://img.shields.io/pypi/l/shadows)](https://github.com/SRSWTI/shadows/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://SRSWTI.github.io/shadows/)

## At a glance

```python
from datetime import datetime, timedelta, timezone

from shadows import Shadow


async def greet(name: str, greeting="Hello") -> None:
    print(f"{greeting}, {name} at {datetime.now()}!")


async with Shadow() as shadows:
    await shadows.add(greet)("Jane")

    now = datetime.now(timezone.utc)
    soon = now + timedelta(seconds=3)
    await shadows.add(greet, when=soon)("John", greeting="Howdy")
```

```python
from shadows import Shadow, Worker

async with Shadow() as shadows:
    async with Worker(shadows) as worker:
        await worker.run_until_finished()
```

```
Hello, Jane at 2025-03-05 13:58:21.552644!
Howdy, John at 2025-03-05 13:58:24.550773!
```

Check out our docs for more [details](http://SRSWTI.github.io/shadows/),
[examples](https://SRSWTI.github.io/shadows/getting-started/), and the [API
reference](https://SRSWTI.github.io/shadows/api-reference/).

## Why `shadows`?

⚡️ Snappy one-way background task processing without any bloat

📅 Schedule immediate or future work seamlessly with the same interface

⏭️ Skip problematic tasks or parameters without redeploying

🌊 Purpose-built for Redis streams

🧩 Fully type-complete and type-aware for your background task functions

💉 Dependency injection like FastAPI, Typer, and FastMCP for reusable resources

## Installing `shadows`

Shadow is [available on PyPI](https://pypi.org/project/shadows/) under the package name
`shadow-task`. It targets Python 3.12 or above.

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install shadows

or

uv add shadows
```

With `pip`:

```bash
pip install shadows
```

Shadow requires a [Redis](http://redis.io/) server with Streams support (which was
introduced in Redis 5.0.0). Shadow is tested with Redis 6 and 7.

# Hacking on `shadows`

We use [`uv`](https://docs.astral.sh/uv/) for project management, so getting set up
should be as simple as cloning the repo and running:

```bash
uv sync
```

The to run the test suite:

```bash
pytest
```

We aim to maintain 100% test coverage, which is required for all PRs to `shadows`. We
believe that `shadows` should stay small, simple, understandable, and reliable, and that
begins with testing all the dusty branches and corners. This will give us the
confidence to upgrade dependencies quickly and to adapt to new versions of Redis over
time.
