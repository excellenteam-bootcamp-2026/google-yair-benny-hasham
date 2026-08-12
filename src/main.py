from src import config
from src.indexer import build_index
from src.search import AutoCompleteEngine


def print_completions(completions):
    if not completions:
        print("No suggestions found")
        return

    print(f"Here are {len(completions)} suggestions")

    for position, completion in enumerate(completions, start=1):
        print(f"{position}. {completion}")


def main():
    if not config.DATA_DIR.exists():
        print(f"Corpus directory not found: {config.DATA_DIR}")
        return

    # The offline phase
    print("Loading the files and preparing the system...")
    trie, store = build_index()
    engine = AutoCompleteEngine(trie, store)

    # The online phase
    print(f"The system is ready. Enter your text ({len(store)} sentences loaded):")
    typed = ""

    while True:
        try:
            # The accumulated text is shown as the prompt, so that the user
            # carries on from where they stopped
            addition = input(typed)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if config.RESET_CHAR in addition:
            typed = ""
            continue

        typed += addition

        if not typed.strip():
            continue

        print_completions(engine.get_best_k_completions(typed))


if __name__ == "__main__":
    main()
