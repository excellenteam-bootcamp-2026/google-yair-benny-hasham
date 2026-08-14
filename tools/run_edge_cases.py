"""
Runs a fixed set of edge-case queries against the real corpus and writes a
timestamped, human-readable report with the output and timing of each case.

Usage: python -m tools.run_edge_cases
"""

import json
import time
from datetime import datetime
from pathlib import Path

from src import config
from src.indexer import build_index
from src.search import AutoCompleteEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
EDGE_CASES_PATH = REPO_ROOT / "tests" / "edge_cases.json"
RESULTS_DIR = REPO_ROOT / "results"


def format_completions(completions):
    if not completions:
        return "No suggestions found"

    lines = [f"Here are {len(completions)} suggestions"]

    for position, completion in enumerate(completions, start=1):
        lines.append(f"{position}. {completion}")

    return "\n".join(lines)


def load_edge_cases():
    with EDGE_CASES_PATH.open(encoding="utf-8") as edge_cases_file:
        return json.load(edge_cases_file)


def run_case(engine, query):
    """Time a single query. Errors are captured, not raised, so one bad case
    doesn't stop the rest of the report from being generated."""
    start = time.perf_counter()

    try:
        completions = engine.get_best_k_completions(query)
        output = format_completions(completions)
    except Exception as error:
        output = f"ERROR: {error!r}"

    elapsed_ms = (time.perf_counter() - start) * 1000

    return output, elapsed_ms


def build_report(cases, sentence_count, run_at):
    lines = [
        "Auto-Complete Edge Case Report",
        f"Run: {run_at:%Y-%m-%d %H:%M:%S}",
        f"Corpus: {sentence_count} sentences",
        "",
    ]
    timings = []

    for position, case in enumerate(cases, start=1):
        output, elapsed_ms = case["output"], case["elapsed_ms"]
        timings.append(elapsed_ms)

        lines.append(f'{position}. [{case["label"]}] "{case["query"]}"')
        lines.append(f"   Time: {elapsed_ms:.2f} ms")
        lines.extend(f"   {line}" for line in output.splitlines())
        lines.append("")

    lines.append(
        f"Summary: {len(cases)} cases, "
        f"avg {sum(timings) / len(timings):.2f}ms, "
        f"min {min(timings):.2f}ms, "
        f"max {max(timings):.2f}ms"
    )

    return "\n".join(lines)


def main():
    if not config.DATA_DIR.exists():
        print(f"Corpus directory not found: {config.DATA_DIR}")
        return

    print("Loading the files and preparing the system...")
    trie, store = build_index()
    engine = AutoCompleteEngine(trie, store)

    edge_cases = load_edge_cases()
    results = []

    for case in edge_cases:
        output, elapsed_ms = run_case(engine, case["query"])
        results.append({**case, "output": output, "elapsed_ms": elapsed_ms})

    run_at = datetime.now()
    report = build_report(results, len(store), run_at)

    RESULTS_DIR.mkdir(exist_ok=True)
    report_path = RESULTS_DIR / f"edge_case_report_{run_at:%Y%m%d_%H%M%S}.txt"
    report_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nSaved to {report_path}")


if __name__ == "__main__":
    main()
