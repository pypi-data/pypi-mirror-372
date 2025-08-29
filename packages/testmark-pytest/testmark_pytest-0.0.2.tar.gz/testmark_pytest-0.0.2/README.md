# testmark-pytest

Python adapter for [TestMark](https://github.com/holdenmatt/testmark) - write language-agnostic tests in Markdown, run them with pytest.

## Installation

```bash
pip install testmark-pytest
```

## Requirements

- Python 3.8+
- Node.js and the global `testmark` CLI from npm (`npm i -g testmark`)

## Usage

Write your tests in Markdown with `<input>` and `<output>` tags (see the [README](https://github.com/holdenmatt/testmark) for details):

```markdown
# Slugify Tests

## Spaces to Dashes
<input>Hello World</input>
<output>hello-world</output>

## Handle Errors
<input></input>
<error>Input cannot be empty</error>
```

Generate pytest tests from your Markdown:

```python
from testmark import testmark
from my_module import slugify

# Generates test_spaces_to_dashes, test_remove_special_characters, etc.
testmark('tests/slugify.test.md', slugify)
```

Run with pytest as normal:

```bash
pytest
```

## How it works

The Python adapter calls the Node.js `testmark` CLI to parse the Markdown file, then dynamically generates pytest test functions. Each heading with `<input>`/`<output>` tags becomes a separate pytest test that can pass or fail independently.