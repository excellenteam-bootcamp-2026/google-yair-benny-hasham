from src import config


def iter_sentences(data_dir=None):
    """
    Walks all text files in the directory tree and returns each line as a sentence.

    Returns triples (path, offset, raw_line) where:
      path     - the file's path relative to the corpus directory
      offset   - the line number in the file (0-based)
      raw_line - the line as it is in the original, including punctuation and case
    """
    if data_dir is None:
        data_dir = config.DATA_DIR

    for path in sorted(data_dir.rglob("*.txt")):
        relative_path = path.relative_to(data_dir).as_posix()

        with path.open(encoding="utf-8", errors="replace") as text_file:
            for offset, raw_line in enumerate(text_file):
                raw_line = raw_line.rstrip("\n").rstrip("\r")

                if raw_line.strip():
                    yield relative_path, offset, raw_line
