class SentenceStore:
    """
    Holds the sentence data outside the tree. The Trie only stores an id, and
    everything needed for output is kept here: the original text, the file
    path, and the line number.

    This is accessed only for the final results, not during the search itself.
    """

    def __init__(self):
        self._raw_lines = []
        self._sources = []
        self._offsets = []

    def add(self, raw_line, source, offset):
        """Adds a sentence and returns its id."""
        self._raw_lines.append(raw_line)
        self._sources.append(source)
        self._offsets.append(offset)

        return len(self._raw_lines) - 1

    def get(self, sentence_id):
        """Returns (raw_line, source, offset) for an id."""
        return (
            self._raw_lines[sentence_id],
            self._sources[sentence_id],
            self._offsets[sentence_id],
        )

    def __len__(self):
        return len(self._raw_lines)
