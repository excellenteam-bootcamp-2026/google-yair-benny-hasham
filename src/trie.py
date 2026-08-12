class Location:
    def __init__(self, source, offset):
        self.source = source
        self.offset = offset


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

        # Every place the word ending at this node was found
        self.locations = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, text, source, offset):
        node = self.root

        for char in text:
            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        node.is_end = True

        location = Location(source, offset)
        node.locations.append(location)
