class SentenceStore:
    """
    Holds the sentence data outside of the trie. The trie stores nothing but
    an id, and everything the output needs lives here: the original text, the
    path of the file and the line number inside it.

    This is read only for the final results, never during the search itself.
    """

    def __init__(self):
        self._raw_lines = []
        self._sources = []
        self._offsets = []

    def add(self, raw_line, source, offset):
        """Store a sentence and return its id."""
        self._raw_lines.append(raw_line)
        self._sources.append(source)
        self._offsets.append(offset)

        return len(self._raw_lines) - 1

    def get(self, sentence_id):
        """Return (raw_line, source, offset) for an id."""
        return (
            self._raw_lines[sentence_id],
            self._sources[sentence_id],
            self._offsets[sentence_id],
        )

    def __len__(self):
        return len(self._raw_lines)
