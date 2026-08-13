from pathlib import Path

# Number of completions returned to the user
MAX_COMPLETIONS = 5

# The character that resets the accumulated text back to the initial state
RESET_CHAR = "#"

# Corpus directory - a directory tree containing text files
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "Archive"

# Each matched character is worth 2 points
POINTS_PER_MATCHED_CHAR = 2

# There is a contradiction in the spec: per the Hebrew examples, the substituted
# character is not counted in the base score ("lihiot o lo" -> 2x10-1=19 for an
# 11-character query), while per the English appendix it is counted
# ("2o be" -> Base=10 for a 5-character query). For insertion and deletion both
# sources agree the character is not counted. This flag allows flipping the behavior.
COUNT_SUBSTITUTED_CHAR = False

# Penalty for substituting a character, by the character's position in the query (0-based)
SUBSTITUTION_PENALTIES = (5, 4, 3, 2)
SUBSTITUTION_PENALTY_REST = 1

# Penalty for inserting or deleting a character, by the character's position in the query (0-based)
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
