# Nanos

![logo](docs/source/_static/nanos_logo.png)

*Nanos* is a collection of small but handy Python utilities: different
functions, classes and mixins. The library has zero dependencies and relies
only on built-in Python modules.

Complete documentation: https://nanos.readthedocs.io/en/latest/index.html

## Features

* **Data Processing** - Utilities for working with data structures (chunking, ID mapping, empty value handling)
* **Date & Time** - Helper functions for common date operations and time measurements
* **Formatting** - Human-readable formatting for data types (file sizes, etc.)
* **Logging** - Simple logging setup and convenient LoggerMixin
* **Zero Dependencies** - Works with just the Python standard library

## Installation

Library is available on PyPI and can be installed using pip:

```bash
pip install nanos
```

## Quick Examples

### Format file sizes

```python
from nanos import fmt

print(fmt.size(1024))        # 1.00 KiB
print(fmt.size(1572864))     # 1.50 MiB
print(fmt.size(3.5 * 10**9)) # 3.26 GiB
```

### Measure execution time

```python
import time
from nanos import time as ntime

with ntime.Timer() as t:
    time.sleep(1.5)

print(t.elapsed)   # 1.5033...
print(t)           # 0:00:01.50
```

### Date helpers

```python
from nanos import dt
import datetime

# Get tomorrow's date in UTC
tomorrow = dt.tomorrow()

# Get yesterday's start/end timestamps
day_start = dt.yesterday_start()
day_end = dt.yesterday_end()
```

### Data processing

```python
from nanos import data

# Split a list into chunks
chunks = data.chunker(range(10), 3)  # [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

# Convert a list of objects to a dict indexed by ID
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
users_by_id = data.idfy(users)  # {1: {"id": 1, "name": "Alice"}, 2: {"id": 2, "name": "Bob"}}

# Remove empty values from nested data
cleaned = data.remove_empty_members({"user": {"name": "Alice", "bio": ""}})  # {"user": {"name": "Alice"}}
```

### Simple logging setup

```python
from nanos import logging

# Get a pre-configured logger with console output
logger = logging.get_simple_logger(name="myapp")
logger.info("Application started")  # 2023-05-01T12:34:56 myapp INFO Application started

# Use LoggerMixin in your classes
class MyService(logging.LoggerMixin):
    def process(self):
        self.logger.debug("Processing started")  # mypackage.MyService DEBUG Processing started
```

## Type Hinting

Nanos is fully typed and includes a `py.typed` marker file for better IDE support.

## License

The library is released under the [Apache License 2.0](LICENSE)
