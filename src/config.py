from pathlib import Path

# How many completions are returned to the user
MAX_COMPLETIONS = 5

# Typing this character clears the accumulated text and returns to the initial state
RESET_CHAR = "#"

# Corpus root: a directory tree holding the text files
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "Archive"

# Every matching character is worth 2 points
POINTS_PER_MATCHED_CHAR = 2

# Penalty for a substituted character, by its position in the query (0-based)
SUBSTITUTION_PENALTIES = (5, 4, 3, 2)
SUBSTITUTION_PENALTY_REST = 1

# Penalty for an added or a missing character, by its position in the query (0-based)
INDEL_PENALTIES = (10, 8, 6, 4)
INDEL_PENALTY_REST = 2


def substitution_penalty(index):
    if index < len(SUBSTITUTION_PENALTIES):
        return SUBSTITUTION_PENALTIES[index]

    return SUBSTITUTION_PENALTY_REST


def indel_penalty(index):
    if index < len(INDEL_PENALTIES):
        return INDEL_PENALTIES[index]

    return INDEL_PENALTY_REST
