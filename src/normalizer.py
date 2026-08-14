import re

# Anything that isn't a letter, digit, or whitespace is treated as punctuation and stripped entirely
_PUNCTUATION = re.compile(r"[^a-z0-9\s]")
_WHITESPACE = re.compile(r"\s+")


def normalize(text):
    """
    Normalizes text for comparison: lowercase, no punctuation, whitespace collapsed to a single space.

    The comparison ignores case and punctuation, and the number of spaces between
    words doesn't matter, so "to be that", "to be, that" and "to be    that" all
    normalize to the same string.
    """
    # Punctuation is removed first and only then whitespace is collapsed, otherwise
    # punctuation surrounded by spaces would leave a double space behind
    text = _PUNCTUATION.sub("", text.lower())
    text = _WHITESPACE.sub(" ", text)

    return text.strip()


def split_words(text):
    """Splits normalized text into a list of words."""
    return text.split()
