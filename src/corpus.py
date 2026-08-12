from src import config


def iter_sentences(data_dir=None):
    """
    Walk the directory tree and yield every line of every text file as a
    sentence.

    Yields (source, offset, raw_line) where:
      source   - the path of the file relative to the corpus root
      offset   - the line number inside that file (0-based)
      raw_line - the line exactly as it appears in the file, punctuation and
                 capitalization included
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
