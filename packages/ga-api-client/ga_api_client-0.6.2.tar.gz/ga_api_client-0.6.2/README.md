# GenieAnalytics Python Client

This package is the official Python client to access GenieAnalytics API server.

## Installation

```
pip install ga-api-client
```

## Linter
- flake8
```
pip install flake8
flake8 --max-complexity=10 --max-line-length=127 .
```

- mypy
```
pip install mypy
mypy .
```

## Import Modules

```python
from ga_api import Repository, HyperLogLog
```

## Top Level Pattern

```python
from ga_api import Repository, System, HyperLogLog
import asyncio
import pandas as pd

async def main():
    try:
        repo = Repository('https://rdlab-214.genie-analytics.com/api', 'api', 'default', 'api123!@#')
        # ...
        # access API server to do whatever you need
        # ...
    finally:
        await repo.close()

if __name__ == '__main__':
    asyncio.run(main())
```
