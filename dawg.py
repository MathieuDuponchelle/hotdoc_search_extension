# This class represents a node in the directed acyclic word graph (DAWG). It
# has a list of edges to other nodes. It has functions for testing whether it
# is equivalent to another node. Nodes are equivalent if they have identical
# edges, and each identical edge leads to identical states. The __hash__ and
# __eq__ functions allow it to be used as a key in a python dictionary.


class DawgNode:
    def __init__(self):
        self.bft_id = 0
        self.bft_last = False
        self.final = False
        self.edges = {}

    def __str__(self):
        arr = []
        if self.final:
            arr.append("1")
        else:
            arr.append("0")

        for (label, node) in self.edges.items():
            arr.append(label)
            arr.append(str(id(node)))

        return "_".join(arr)

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

class Dawg:

    def __init__(self):
        self.previous_word = ""
        self.root = DawgNode()

    def insert(self, word, data):
        if word == self.previous_word:
            return

        elif word < self.previous_word:
            raise Exception("Error: Words must be inserted in alphabetical " +
                            "order.")

        # find common prefix between word and previous word
        common_prefix = 0
        node = self.root
        for i in range(min(len(word), len(self.previous_word))):
            letter = word[i]
            if letter != self.previous_word[i]:
                break
            node = node.edges[letter]
            common_prefix += 1

        for letter in word[common_prefix:]:
            nextNode = DawgNode()
            node.edges[letter] = nextNode
            node = nextNode

        node.final = True
        self.previous_word = word

    def lookup(self, word):
        node = self.root
        for letter in word:
            if letter not in node.edges:
                return False
            for label, child in sorted(node.edges.items()):
                if label == letter:
                    node = child
                    break

        if node.final:
            return True

    def search(self, word, maxCost):
        # build first row
        currentRow = range(len(word) + 1)

        results = []

        # recursively search each branch of the trie
        for letter in self.root.edges:
            self.searchRecursive(self.root.edges[letter], letter, word, currentRow,
                                 results, maxCost, letter)

        return results

    # This recursive helper is used by the search function above. It assumes that
    # the previousRow has been filled in already.
    def searchRecursive(self, node, letter, word, previousRow, results, maxCost,
                        currentWord):
        columns = len(word) + 1
        currentRow = [previousRow[0] + 1]

        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in range(1, columns):
            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1

            if word[column - 1] != letter:
                replaceCost = previousRow[column - 1] + 1
            else:
                replaceCost = previousRow[column - 1]

            currentRow.append(min(insertCost, deleteCost, replaceCost))

        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.final:
            results.append((currentWord, currentRow[-1]))

        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie
        if min(currentRow) <= maxCost:
            for letter in node.edges:
                self.searchRecursive(node.edges[letter], letter, word, currentRow,
                                     results, maxCost, currentWord + letter)

    def unroll(self, node):
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
                node.letter = letter
                unrolled.append(node)
                queue.append(new_path)

        return unrolled

    def dump_node(self, node):
        first_child_id = 0
        if node.edges:
            first_child_id = sorted(node.edges.items())[0][1].bft_id
        res = int(first_child_id) << 7
        if node.bft_last:
            res |= (1 << 6)
        if node.final:
            res |= (1 << 5)
        res |= self.clamp_letter(node.letter)
        self.dump_file.write(res.to_bytes(4, byteorder='big', signed=False))

    def dump(self):
        with open ("dumped.dawg", 'wb') as self.dump_file:
            res = int(1) << 7
            res |= (1 << 6)
            res |= 29
            self.dump_file.write(res.to_bytes(4, byteorder='big', signed=False))
            unrolled = self.unroll(self.root)
            for node in unrolled:
                self.dump_node(node)

    def clamp_letter(self, letter):
        return (ord(letter) - ord('a'))

LETTER_MASK = 0x1F
FINAL_MASK = 1 << 5
BFT_LAST_MASK = 1 << 6

class FrozenDawgNode:
    def __init__(self, dawg, bnode):
        self.letter = chr(ord('a') + (bnode & LETTER_MASK))
        self.final = bool(bnode & FINAL_MASK)
        self.bft_last = bool(bnode & BFT_LAST_MASK)
        self.first_child_id = int(bnode >> 7)
        self.dawg = dawg
        self.edges = None

    def get_edges(self):
        if self.edges is not None:
            return self.edges

        edges = {}
        next_id = self.first_child_id
        while next_id:
            edge = self.dawg.get_node_by_index(next_id)
            if edge.bft_last:
                next_id = 0
            else:
                next_id += 1
            edges[edge.letter] = edge

        self.edges = edges
        return edges

    def __repr__(self):
        return ' '.join([str(self.first_child_id), str(self.bft_last),
            str(self.final), str(self.letter)])

class FrozenDawg:
    def __init__(self, data):
        self.data = data
        self.root = self.get_node_by_index(0) 

    def get_node_by_index(self, index):
        bnode = int.from_bytes(self.data[index * 4:index * 4 + 4],
                byteorder='big')
        fnode = FrozenDawgNode(self, bnode)
        return fnode

    def lookup(self, word):
        node = self.root
        for letter in word:
            edges = node.get_edges()
            if letter not in edges:
                return False
            for label, child in sorted(edges.items()):
                if label == letter:
                    node = child
                    break

        if node.final:
            return True

        return False

if __name__ == '__main__':
    import sys, re
    dawg = Dawg()
    WordCount = 0

    DICT = 'somewords.txt'

    with open(DICT, 'r') as f:
        words = [w.lower() for w in f.read().split()]

    words.sort()
    for word in words:
        if not re.match(r'^[a-z]+$', word):
            continue

        WordCount += 1
        # insert all words, using the reversed version as the data associated with
        # it
        dawg.insert(word, ''.join(reversed(word)))
        if (WordCount % 100) == 0:
            sys.stderr.write("{0}\r".format(WordCount))

    dawg.dump()

    with open('dumped.dawg', 'rb') as f:
        data = f.read()

    fdawg = FrozenDawg(data)

    # True
    print (dawg.lookup('abaff'))
    # True
    print (fdawg.lookup('abaff'))

    # False
    print (dawg.lookup('completenonsense'))
    # False
    print (fdawg.lookup('completenonsense'))
