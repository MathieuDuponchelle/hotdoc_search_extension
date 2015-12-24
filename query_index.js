LETTER_MASK = 0x1F;
FINAL_MASK = 1 << 5;
BFT_LAST_MASK = 1 << 6;

function TrieNode(trie, data) {
	this.edges = undefined;
	this.trie = trie;
	this.letter = String.fromCharCode((data & LETTER_MASK) + 'a'.charCodeAt(0));

	this.is_final = false;
	if (data & FINAL_MASK) {
		this.is_final = true;
	}

	this.bft_last = false;
	if (data & BFT_LAST_MASK) {
		this.bft_last = true;
	}

	this.first_child_id = data >> 7;
}

TrieNode.prototype.get_edges = function() {
	if (this.edges != undefined) {
		return this.edges;
	}

	this.edges = {}

	var next_id = this.first_child_id;

	while (next_id != 0) {
		var edge = this.trie.get_node_by_index(next_id);
		if (edge.bft_last) {
			next_id = 0;
		} else {
			next_id += 1;
		}
		this.edges[edge.letter] = edge;
	}

	return this.edges;
};

function Trie(data) {
	this.data = data;
	this.root = this.get_node_by_index(0);
}

Trie.prototype.get_node_by_index = function(idx) {
	return new TrieNode(this, this.data[idx]); 
};

Trie.prototype.lookup = function (word) {
	node = this.root;

	for (idx in word) {
		letter = word[idx];

		edges = node.get_edges();
		if (letter in edges) {
			node = edges[letter];
		} else {
			return false;
		}
	}

	if (node.is_final) {
		return true;
	}

	return false;
};

module.exports = Trie;
