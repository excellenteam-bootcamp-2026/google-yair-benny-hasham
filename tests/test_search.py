import pytest

from src.normalizer import normalize, split_words
from src.search import AutoCompleteEngine
from src.sentence_store import SentenceStore
from src.trie import Trie

HAMLET = "To be or not to be, that is the question."


def build_engine(sentences):
    trie = Trie()
    store = SentenceStore()

    for offset, raw_line in enumerate(sentences):
        sentence_id = store.add(raw_line, "test.txt", offset)

        for word_offset, word in enumerate(split_words(normalize(raw_line))):
            trie.insert(word, sentence_id, word_offset)

    return AutoCompleteEngine(trie, store)


def top_score(engine, query):
    results = engine.get_best_k_completions(query)

    return results[0].score if results else None


# The examples from the appendix. The two substitution cases score 2 points
# lower here, following the main specification rather than the appendix table.
# See the comment in scorer.
@pytest.mark.parametrize(
    "query, expected",
    [
        ("To be", 10),
        ("or Not", 12),
        ("be, that", 14),
        ("or knot", 8),
        ("2o be", 3),
        ("to pe", 6),
    ],
)
def test_scores_from_the_specification(query, expected):
    engine = build_engine([HAMLET])

    assert top_score(engine, query) == expected


def test_two_corrections_are_not_a_match():
    engine = build_engine([HAMLET])

    assert engine.get_best_k_completions("not be") == []


def test_match_in_the_middle_of_the_sentence():
    engine = build_engine([HAMLET])
    results = engine.get_best_k_completions("that is")

    assert len(results) == 1
    assert results[0].completed_sentence == HAMLET
    assert results[0].score == 14


def test_result_carries_the_original_line_and_its_position():
    engine = build_engine(["nothing here", HAMLET])
    result = engine.get_best_k_completions("or not")[0]

    assert result.completed_sentence == HAMLET
    assert result.source_text == "test.txt"
    assert result.offset == 1


def test_equal_scores_are_ordered_alphabetically():
    engine = build_engine(["Zebra to be here.", "Apple to be here.", "Mango to be here."])
    results = engine.get_best_k_completions("to be")

    assert [result.score for result in results] == [10, 10, 10]
    assert [result.completed_sentence for result in results] == [
        "Apple to be here.",
        "Mango to be here.",
        "Zebra to be here.",
    ]


def test_at_most_five_completions_are_returned():
    engine = build_engine([f"sentence {index} to be here." for index in range(9)])

    assert len(engine.get_best_k_completions("to be")) == 5


def test_exact_matches_outrank_corrected_ones():
    engine = build_engine(["the question stands.", "the quastion stands."])
    results = engine.get_best_k_completions("the question")

    assert [result.completed_sentence for result in results] == [
        "the question stands.",
        "the quastion stands.",
    ]
    assert [result.score for result in results] == [24, 21]


def test_swapped_letters_need_two_corrections_and_are_not_a_match():
    # qeustion against question is a swap, which takes two corrections
    engine = build_engine(["the qeustion stands."])

    assert engine.get_best_k_completions("the question") == []
