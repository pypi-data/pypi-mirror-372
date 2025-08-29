# TestMark (Pytest Adapter)

Minimal Python adapter around the Node `testmark` parser.

## Requirements

- Python 3.8+
- Node.js and the global `testmark` CLI from npm (`npm i -g testmark`)

## Usage

Pytest adapter:

```python
from testmark import testmark
from slugify import slugify

testmark('examples/slugify.test.md', slugify)
```

## How it works

The Python package defers to the Node CLI for parsing and expects a global `testmark` binary on PATH.

## Running Tests

To test the Python adapter:

```bash
cd adapters/pytest
uv sync  # Install venv/pytest
uv run pytest
```
