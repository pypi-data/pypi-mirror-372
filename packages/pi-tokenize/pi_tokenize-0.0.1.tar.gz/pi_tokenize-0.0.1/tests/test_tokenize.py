"""
Tests for pi_tokenize package.
"""

import io
from pi_tokenize import tokenize  # pyright: ignore[reportAttributeAccessIssue]


def test_basic_tokenization():
    """Test basic tokenization functionality."""
    a = io.BytesIO(b"from a import b")
    tokens = list(tokenize.tokenize(a.readline))

    # Should get several tokens for this simple import statement
    assert len(tokens) > 0

    # Basic validation - should have NAME tokens for 'from', 'a', 'import', 'b'
    token_strings = [
        token.string for token in tokens if token.type == tokenize.NAME
    ]
    expected_names = ["from", "a", "import", "b"]

    for name in expected_names:
        assert name in token_strings, (
            f"Expected token '{name}' not found in {token_strings}"
        )


def test_tokenize_simple_expression():
    """Test tokenization of a simple expression."""
    code = b"x = 42"
    a = io.BytesIO(code)
    tokens = list(tokenize.tokenize(a.readline))

    # Should have tokens for identifier, operator, number
    assert len(tokens) > 0


def test_tokenize_empty_input():
    """Test tokenization of empty input."""
    a = io.BytesIO(b"")
    tokens = list(tokenize.tokenize(a.readline))

    # Should at least have ENCODING and ENDMARKER tokens
    assert len(tokens) >= 2
