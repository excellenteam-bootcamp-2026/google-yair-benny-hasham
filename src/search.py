from src import config
from src.fuzzy_trie import collect_locations, find_word_matches
from src.models import AutoCompleteData
from src.normalizer import normalize, split_words
from src.scorer import NO_EDIT, score_of


def _word_offsets(words):
    """Where each word starts inside the normalized query."""
    offsets = []
    position = 0

    for word in words:
        offsets.append(position)
        position += len(word) + 1

    return offsets


def _intersect(locations_per_word):
    """
    Return every (sentence_id, start) pair where all the words of the query
    appear consecutively in the sentence.

    The word at position index in the query has to sit at start + index in the
    sentence, so subtracting the index from the position of each word brings
    them all onto the same key.
    """
    order = sorted(enumerate(locations_per_word), key=lambda pair: len(pair[1]))
    candidates = None

    for index, locations in order:
        starts = {(location.source, location.offset - index) for location in locations}

        if candidates is None:
            candidates = starts
        else:
            candidates &= starts

        if not candidates:
            return set()

    return candidates


class AutoCompleteEngine:
    def __init__(self, trie, store):
        self.trie = trie
        self.store = store

    def get_best_k_completions(self, prefix, k=None):
        if k is None:
            k = config.MAX_COMPLETIONS

        words = split_words(normalize(prefix))

        if not words:
            return []

        query_length = len(" ".join(words))
        exact = self._exact_locations(words)
        best = {}

        for plan_score, word_index, locations in self._build_plans(words, query_length):
            if self._can_stop(best, k, plan_score):
                break

            per_word = list(exact)

            if word_index is not None:
                per_word[word_index] = locations

            for sentence_id, _start in _intersect(per_word):
                if best.get(sentence_id, -1) < plan_score:
                    best[sentence_id] = plan_score

        return self._top(best, k)

    def _exact_locations(self, words):
        """The locations of every query word matched exactly, uncorrected."""
        last = len(words) - 1
        result = []

        for index, word in enumerate(words):
            locations = []

            for node, _kind, _at in find_word_matches(self.trie.root, word, False):
                locations.extend(collect_locations(node, index == last))

            result.append(locations)

        return result

    def _build_plans(self, words, query_length):
        """
        Build the possible plans, ordered by descending score.

        A plan is the choice of which query word carries the single correction
        that is allowed, if any. Since the score follows from the kind of the
        correction and its position alone, every result a single plan produces
        carries the same score.
        """
        last = len(words) - 1
        offsets = _word_offsets(words)
        plans = {(None, score_of(query_length, NO_EDIT, 0)): None}

        for index, word in enumerate(words):
            for node, kind, at in find_word_matches(self.trie.root, word, True):
                if kind == NO_EDIT:
                    continue

                locations = collect_locations(node, index == last)

                if not locations:
                    continue

                key = (index, score_of(query_length, kind, offsets[index] + at))
                plans.setdefault(key, []).extend(locations)

        ordered = sorted(plans.items(), key=lambda item: -item[0][1])

        return [(value, index, locations) for (index, value), locations in ordered]

    @staticmethod
    def _can_stop(best, k, next_score):
        """
        Plans are ordered by descending score, so once k results are in hand
        and all of them beat the next plan, there is nothing left to gain.
        """
        if len(best) < k:
            return False

        return sorted(best.values(), reverse=True)[k - 1] > next_score

    def _top(self, best, k):
        """
        Build the final results. This is the only place the sentence text is
        read, and only for the highest scoring groups needed to fill k results.
        """
        by_score = {}

        for sentence_id, value in best.items():
            by_score.setdefault(value, []).append(sentence_id)

        results = []

        for value in sorted(by_score, reverse=True):
            for sentence_id in by_score[value]:
                raw_line, source, offset = self.store.get(sentence_id)
                results.append(AutoCompleteData(raw_line, source, offset, value))

            if len(results) >= k:
                break

        results.sort(key=AutoCompleteData.sort_key)

        return results[:k]
