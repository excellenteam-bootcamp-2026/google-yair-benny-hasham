from src.scorer import DELETION, INSERTION, NO_EDIT, SUBSTITUTION


def _walk(node, word, start, end):
    """Exact walk over word[start:end]. Returns the node or None."""
    for index in range(start, end):
        node = node.children.get(word[index])

        if node is None:
            return None

    return node


def _prefix_nodes(root, word):
    """Returns the chain of nodes along the word, up to the point where it breaks off."""
    nodes = [root]
    node = root

    for char in word:
        node = node.children.get(char)

        if node is None:
            break

        nodes.append(node)

    return nodes


def find_word_matches(root, word, allow_edit):
    """
    Searches for a word in the tree with at most one correction.

    Returns a list of (node, edit_kind, edit_index), where edit_index is the
    position of the correction within the typed word.
    """
    matches = []
    length = len(word)
    prefixes = _prefix_nodes(root, word)

    if len(prefixes) == length + 1:
        matches.append((prefixes[length], NO_EDIT, 0))

    if not allow_edit:
        return matches

    for index in range(min(length + 1, len(prefixes))):
        node = prefixes[index]

        if index < length:
            # Substituting the character at position index with any other character
            for char, child in node.children.items():
                if char == word[index]:
                    continue

                found = _walk(child, word, index + 1, length)

                if found is not None:
                    matches.append((found, SUBSTITUTION, index))

            # The character at position index is extra - skip over it
            found = _walk(node, word, index + 1, length)

            if found is not None:
                matches.append((found, INSERTION, index))

        # A character is missing before position index - fill it in from the tree
        for child in node.children.values():
            found = _walk(child, word, index, length)

            if found is not None:
                matches.append((found, DELETION, index))

    return matches


def collect_locations(node, is_prefix):
    """
    Collects the locations of a node.

    A word that isn't the last one in the query requires a match to a whole
    word, so only the locations of the node itself are taken. The last word
    is a prefix of a word, so all its descendants are collected too.
    """
    if not is_prefix:
        return node.locations if node.is_end else []

    locations = []
    stack = [node]

    while stack:
        current = stack.pop()

        if current.is_end:
            locations.extend(current.locations)

        stack.extend(current.children.values())

    return locations
