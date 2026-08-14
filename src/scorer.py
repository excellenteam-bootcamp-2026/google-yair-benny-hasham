from src import config

# The possible correction kinds. INSERTION is an extra character in the
# query that doesn't exist in the sentence, and DELETION is a character that
# exists in the sentence and is missing from the query.
NO_EDIT = "none"
SUBSTITUTION = "substitution"
INSERTION = "insertion"
DELETION = "deletion"


def score_of(query_length, edit_kind, edit_index):
    """
    Computes a score based on the query length, the correction kind, and its
    position within the query.

    The sentence text isn't needed: the correction kind and its position are
    already known while walking the tree, and from them both the number of
    matched characters and the penalty are derived.
    """
    if edit_kind == NO_EDIT:
        return config.POINTS_PER_MATCHED_CHAR * query_length

    if edit_kind == SUBSTITUTION:
        matched = query_length if config.COUNT_SUBSTITUTED_CHAR else query_length - 1
        penalty = config.substitution_penalty(edit_index)
    elif edit_kind == INSERTION:
        # The extra character isn't counted as a matched character
        matched = query_length - 1
        penalty = config.indel_penalty(edit_index)
    else:
        # All query characters match, only a sentence character is missing from it
        matched = query_length
        penalty = config.indel_penalty(edit_index)

    return config.POINTS_PER_MATCHED_CHAR * matched - penalty
