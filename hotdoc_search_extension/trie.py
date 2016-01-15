# This class represents a node in the trie. It
# has a list of edges to other nodes.

import base64
import struct
import os

LETTER_MASK = 0x7F
FINAL_MASK = 1 << 7
BFT_LAST_MASK = 1 << 8

def clamp_letter(letter):
    return (ord(letter) - ord('a'))

class TrieNode:
    def __init__(self, trie, letter):
        self.bft_id = 0
        self.first_child_id = 0
        self.bft_last = False
        self.final = False
        self._edges = {}
        self.letter = letter
        self._trie = trie

    @property
    def edges(self):
        if self._edges is not None:
            return self._edges

        self._edges = {}

        next_id = self.first_child_id

        while next_id:
            edge = self._trie.get_node_by_index(next_id)
            if edge.bft_last:
                next_id = 0
            else:
                next_id += 1
            self._edges[edge.letter] = edge

        return self._edges

    @classmethod
    def from_binary(cls, trie, bdata):
        letter = chr(ord('a') + (bdata & LETTER_MASK))

        res = cls(trie, letter)

        res.final = bool(bdata & FINAL_MASK)
        res.bft_last = bool(bdata & BFT_LAST_MASK)
        res.first_child_id = int(bdata >> 9)
        res._edges = None
        return res

    def to_binary(self):
        first_child_id = 0
        if self.edges:
            first_child_id = sorted(self.edges.items())[0][1].bft_id
        res = int(first_child_id) << 9
        if self.bft_last:
            res |= (BFT_LAST_MASK)
        if self.final:
            res |= (FINAL_MASK)
        res |= clamp_letter(self.letter)
        return res

class Trie:
    def __init__(self):
        self._root = TrieNode(self, chr(127))
        self._binary_data = None

    @classmethod
    def from_file(cls, filename):
        res = cls()

        with open(filename, 'rb') as f:
            s = os.path.getsize(filename) / 4
            format_string = '>%dI' % s
            res._binary_data = struct.unpack(format_string, f.read())

        res._root = res.get_node_by_index(0)
        return res

    def insert(self, word):
        # find common prefix between word and previous word
        common_prefix = 0
        node = self._root
        for letter in word:
            if letter in node.edges:
                node = node.edges[letter]
            else:
                break
            common_prefix += 1

        for letter in word[common_prefix:]:
            nextNode = TrieNode(self, letter)
            node.edges[letter] = nextNode
            node = nextNode

        node.final = True

    def remove(self, word):
        if (len(word)) == 0:
            parent = None
        else:
            parent = self.lookup(word[:-1])

        if not parent:
            return False

        node = parent.edges.get(word[-1])  

        if not node:
            return False

        node.final = False
        if not node.edges:
            parent.edges.pop(word[-1])

        return True

    def lookup(self, word):
        node = self._root
        for letter in word:
            edges = node.edges
            if letter not in edges:
                return None
            node = edges[letter]

        return node

    def exists(self, word):
        node = self.lookup(word)
        return bool(node and node.final)

    def search(self, word, max_cost):
        # build first row
        current_row = range(len(word) + 1)

        results = []

        # recursively search each branch of the trie
        for letter in self._root.edges:
            self._search_recursive(self._root.edges[letter], letter, word, current_row,
                                 results, max_cost, letter)

        return results

    # This recursive helper is used by the search function above. It assumes that
    # the previous_row has been filled in already.
    def _search_recursive(self, node, letter, word, previous_row, results, max_cost,
                        currentWord):
        columns = len(word) + 1
        current_row = [previous_row[0] + 1]

        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in range(1, columns):
            insertCost = current_row[column - 1] + 1
            deleteCost = previous_row[column] + 1

            if word[column - 1] != letter:
                replaceCost = previous_row[column - 1] + 1
            else:
                replaceCost = previous_row[column - 1]

            current_row.append(min(insertCost, deleteCost, replaceCost))

        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if current_row[-1] <= max_cost and node.final:
            results.append((currentWord, current_row[-1]))

        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie
        if min(current_row) <= max_cost:
            for letter in node.edges:
                self._search_recursive(node.edges[letter], letter, word, current_row,
                                     results, max_cost, currentWord + letter)

    def get_node_by_index(self, index):
        assert(self._binary_data is not None)

        bnode = self._binary_data[index]
        return TrieNode.from_binary(self, bnode)

    def encode(self):
        data = []
        res = int(1) << 9
        res |= (BFT_LAST_MASK)
        res |= 30
        data.append(res)
        unrolled = self._unroll(self._root)

        if (len(unrolled) >= 2 ** 23):
            raise OverflowError("Too many nodes would need to be encoded")

        for node in unrolled:
            self._encode_node(node, data)
        format_string = ">%dI" % len(data)
        res = struct.pack(format_string, *data)
        b64data = base64.b64encode(str(res))
        return res, b64data

    def to_file(self, raw_filename, js_filename=None):
        data, b64_data = self.encode()
        with open (raw_filename, 'wb') as f:
            f.write(data)

        if js_filename is not None:
            with open(js_filename, 'wb') as f:
                f.write(bytes(b"var trie_data=\""))
                f.write(b64_data)
                f.write(bytes(b"\";"))

    def _unroll(self, node):
        unrolled = []
        node.letter = None
        queue = [[node]]
        bft_id = 0

        while queue:
            path = queue.pop(0)
            vertex = path[-1]
            i = 0
            cnodes = sorted(vertex.edges.items())
            l = len(cnodes)
            for letter, node in cnodes:
                i += 1
                bft_id += 1

                node.bft_id = bft_id
                node.bft_last = False
                if i == l:
                    node.bft_last = True

                new_path = list(path)
                new_path.append(node)
                unrolled.append(node)
                queue.append(new_path)

        return unrolled

    def _encode_node(self, node, data):
        bin_node = node.to_binary()
        data.append(bin_node)
