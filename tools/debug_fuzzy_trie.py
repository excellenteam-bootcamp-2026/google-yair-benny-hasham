"""
Small standalone entry point with a tiny in-memory corpus, for stepping
through fuzzy_trie.py (and the rest of the search path) in the debugger.

Set a breakpoint wherever you want (e.g. fuzzy_trie.py:53, 63 or 69,
search.py, scorer.py) then run this file with "Debug Python File" (F5).

Edit CORPUS and QUERY below to try different cases.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fuzzy_trie import find_word_matches
from src.normalizer import normalize, split_words
from src.search import AutoCompleteEngine
from src.sentence_store import SentenceStore
from src.trie import Trie

CORPUS = [
    "To be or not to be, that is the question.",
    "A bee landed on the flower.",
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
]

QUERY = "to pe"


def build_engine(sentences):
    trie = Trie()
    store = SentenceStore()

    for offset, raw_line in enumerate(sentences):
        sentence_id = store.add(raw_line, "demo.txt", offset)

        for word_offset, word in enumerate(split_words(normalize(raw_line))):
            trie.insert(word, sentence_id, word_offset)

    return trie, store


def main():
    trie, store = build_engine(CORPUS)
    engine = AutoCompleteEngine(trie, store)

    # Low-level: look up a single word straight in the trie, with at most
    # one correction. Good spot for a breakpoint inside find_word_matches
    # itself - step through with a single word like "pe" or "th".
    word = split_words(normalize(QUERY))[-1]
    matches = find_word_matches(trie.root, word, True)

    print(f"find_word_matches(root, {word!r}, allow_edit=True) -> {len(matches)} match(es)")
    for node, kind, index in matches:
        print(f"  kind={kind!r} index={index} locations={[loc.__dict__ for loc in node.locations]}")

    # High-level: the full query path, exercising _build_plans/_intersect/_top
    # in search.py on top of find_word_matches.
    print(f"\nengine.get_best_k_completions({QUERY!r})")
    for result in engine.get_best_k_completions(QUERY):
        print(f"  {result}")


if __name__ == "__main__":
    main()
