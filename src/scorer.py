from src import config

# The kinds of correction a query may need. INSERTION is a character that the
# query has and the sentence does not, DELETION is a character that the
# sentence has and the query is missing.
NO_EDIT = "none"
SUBSTITUTION = "substitution"
INSERTION = "insertion"
DELETION = "deletion"


def score_of(query_length, edit_kind, edit_index):
    """
    Score a match from the length of the query, the kind of correction and the
    position of that correction inside the query.

    The sentence text is never needed: both the kind and the position of the
    correction are already known while walking the trie, and the number of
    matching characters and the penalty follow from them.
    """
    if edit_kind == NO_EDIT:
        return config.POINTS_PER_MATCHED_CHAR * query_length

    if edit_kind == SUBSTITUTION:
        # The substituted character is not counted as a match. The English
        # appendix scores its two substitution examples 2 points higher, but
        # the main specification is self consistent and is what we follow.
        matched = query_length - 1
        penalty = config.substitution_penalty(edit_index)
    elif edit_kind == INSERTION:
        # The extra character in the query is not counted as a match
        matched = query_length - 1
        penalty = config.indel_penalty(edit_index)
    else:
        # Every character of the query matches, only a character of the
        # sentence is missing from it
        matched = query_length
        penalty = config.indel_penalty(edit_index)

    return config.POINTS_PER_MATCHED_CHAR * matched - penalty
