"""Test the TestMark Python adapter on the slugify example tests."""
import re
from testmark import testmark


def slugify(text: str) -> str:
    """
    Example slugify function to demonstrate TestMark
    
    Converts text to URL-friendly slugs.
    This could be any string -> string function, in real usage.
    """
    if text == '':
        raise Exception('Input cannot be empty')
    
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Remove special chars (ASCII only)
    text = re.sub(r'\s+', '-', text)          # Replace spaces with dashes
    text = re.sub(r'-+', '-', text)           # Collapse multiple dashes
    text = re.sub(r'^-+|-+$', '', text)       # Remove leading/trailing dashes
    
    return text


# Generate pytest tests from the markdown file
testmark('../../examples/slugify.test.md', slugify)

