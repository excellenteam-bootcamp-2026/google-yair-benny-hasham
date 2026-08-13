from src.corpus import iter_sentences
from src.normalizer import normalize, split_words
from src.sentence_store import SentenceStore
from src.trie import Trie


def build_index(data_dir=None):
    """
    The offline stage: reads all text files and builds the data structures.

    Every normalized word is inserted into the Trie, with its Location
    pointing at the sentence id and at the word's position within that sentence.

    Returns (trie, store).
    """
    trie = Trie()
    store = SentenceStore()

    for source, offset, raw_line in iter_sentences(data_dir):
        normalized = normalize(raw_line)

        if not normalized:
            continue

        sentence_id = store.add(raw_line, source, offset)

        for word_offset, word in enumerate(split_words(normalized)):
            trie.insert(word, sentence_id, word_offset)

    return trie, store
