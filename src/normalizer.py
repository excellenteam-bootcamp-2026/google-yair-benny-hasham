import re

# Anything that is not a letter, a digit or whitespace counts as punctuation
# and is dropped entirely
_PUNCTUATION = re.compile(r"[^a-z0-9\s]")
_WHITESPACE = re.compile(r"\s+")


def normalize(text):
    """
    Normalize text for comparison: lowercase, no punctuation, and runs of
    whitespace collapsed into a single space.

    Matching ignores case and punctuation, and the number of spaces between
    words does not matter, so "to be, that", "to be that" and "to be    that"
    all normalize to the same string.
    """
    # Punctuation is removed before whitespace is collapsed, otherwise
    # punctuation surrounded by spaces leaves a double space behind
    text = _PUNCTUATION.sub("", text.lower())
    text = _WHITESPACE.sub(" ", text)

    return text.strip()


def split_words(text):
    """Split normalized text into its words."""
    return text.split()
