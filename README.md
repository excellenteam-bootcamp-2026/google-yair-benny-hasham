# Sentence Autocomplete

A sentence-level autocomplete engine: type a partial phrase and get back the
best-matching sentences from a text corpus, tolerating **at most one typo**
(a single substitution, insertion, or deletion) anywhere in the query.
Results are ranked by a scoring formula that rewards matched characters and
penalizes a correction by how early it falls in the query.

## How it works

- **Indexing** (`src/indexer.py`, `src/trie.py`) — every corpus line is split
  into words, and each word is inserted into a shared trie. Every place a word
  occurs is recorded as a `(sentence_id, word_position)` location.
- **Exact + fuzzy lookup** (`src/fuzzy_trie.py`) — a query word is looked up
  exactly, and, allowing one edit, fuzzily: substituting, inserting, or
  deleting a single character while the rest of the word must still match
  exactly. Only one query word carries the correction at a time.
- **Matching** (`src/search.py`) — candidate word locations are intersected so
  that every query word lines up at consecutive positions in the same
  sentence. The one allowed correction is tried once per word, and the best
  scoring plan wins.
- **Scoring** (`src/scorer.py`) — see [Scoring rules](#scoring-rules) below.

## Requirements

Python 3.11+, standard library only. `pytest` is used to run the test suite
(no other dependencies, no `requirements.txt`).

## Corpus data

The engine indexes every `*.txt` file found recursively under a corpus
directory (default: `data/Archive/`, see `config.DATA_DIR`). Each non-blank
line of each file is treated as one candidate sentence; blank lines are
skipped. Files are read as UTF-8, with invalid byte sequences replaced rather
than raising.

## Usage

Run from the repository root, as a module:

```bash
python -m src.main
```

This builds the index from `data/Archive/` and then starts an interactive
session. The text you've typed so far becomes the prompt, so each line you
enter continues from there — press `#` at any point to clear it and start
over. Press `Ctrl+D` (or `Ctrl+C`) to exit.

```
Loading the files and preparing the system...
The system is ready. Enter your text (2391950 sentences loaded):
to be
Here are 5 suggestions
1. to be or not to be (hamlet.txt 120)
2. ...
```

If no sentence matches, it prints `No suggestions found`.

## Configuration

All tunables live in `src/config.py`:

| Constant | Value | Meaning |
|---|---|---|
| `MAX_COMPLETIONS` | `5` | Max suggestions returned per query |
| `RESET_CHAR` | `"#"` | Typing this clears the accumulated input |
| `DATA_DIR` | `data/Archive/` | Corpus root directory |
| `POINTS_PER_MATCHED_CHAR` | `2` | Points per matched character |
| `COUNT_SUBSTITUTED_CHAR` | `False` | Whether a substituted character still counts as matched |
| `SUBSTITUTION_PENALTIES` | `(5, 4, 3, 2)` | Penalty by position (0-based) of a substitution, positions ≥ 4 use `SUBSTITUTION_PENALTY_REST = 1` |
| `INDEL_PENALTIES` | `(10, 8, 6, 4)` | Penalty by position (0-based) of an insertion/deletion, positions ≥ 4 use `INDEL_PENALTY_REST = 2` |

`COUNT_SUBSTITUTED_CHAR` exists because the assignment's two reference
sources disagree on whether a substituted character counts toward the base
score; the code comment in `config.py` walks through both worked examples.
The default (`False`) is what the test suite is written against.

## Scoring rules

At most one correction is allowed per query, across all of its words (two
typos, or a transposition, will not match). A result's score is:

```
matched_chars * POINTS_PER_MATCHED_CHAR - penalty
```

- **No edit**: every character counts as matched, no penalty.
- **Substitution**: `query_length - 1` (or `query_length`, depending on
  `COUNT_SUBSTITUTED_CHAR`) characters matched, penalized by
  `substitution_penalty(edit_index)`.
- **Insertion** (query has an extra character): `query_length - 1` matched,
  penalized by `indel_penalty(edit_index)`.
- **Deletion** (query is missing a character): all of `query_length` matched,
  penalized by `indel_penalty(edit_index)`.

Ties are broken alphabetically by the completed sentence
(`AutoCompleteData.sort_key`).

## Testing

```bash
pytest
```

Runs `tests/test_normalizer.py` and `tests/test_search.py` from the repo
root. No pytest config file or CI is set up.

Two auxiliary dev tools, not part of the test suite:
- `python -m tools.run_edge_cases` — runs the queries in
  `tests/edge_cases.json` against the real corpus and writes a timestamped
  report to `results/`.
- `python tools/debug_fuzzy_trie.py` — a small hardcoded corpus for stepping
  through `fuzzy_trie.py` in a debugger.

## Project structure

```
src/
  main.py            interactive entry point
  config.py           tunable constants
  corpus.py            walks the corpus directory into (source, offset, line)
  indexer.py           builds the trie + sentence store from the corpus
  trie.py             trie node + Location
  fuzzy_trie.py        exact and single-edit trie lookup
  normalizer.py         lowercases / strips punctuation, splits into words
  scorer.py            turns an edit kind + position into a score
  search.py            ties it together: plans, intersection, ranking
  sentence_store.py    id -> (raw_line, source, offset) lookup
  models.py            AutoCompleteData result type
tests/
  test_normalizer.py
  test_search.py
  edge_cases.json      fixed query batch used by tools/run_edge_cases.py
tools/
  run_edge_cases.py    perf/smoke report against the real corpus
  debug_fuzzy_trie.py  debugger entry point with a tiny in-memory corpus
data/Archive/          the corpus (*.txt files, any nesting)
results/               timestamped reports from tools/run_edge_cases.py
```

## Performance

Against the real corpus (`data/Archive/`, ~2.39M sentences), the most recent
optimization pass brought worst-case query latency from 11.0s to 0.9s for a
single common letter, and from 7.3s to 3.0s for a six-word phrase, with no
change to the sentences or scores returned. See `results/` for full reports.
